#include <Arduino.h>
#include <LoRa.h>
#include <SPI.h>
#include <string.h>

#include "config.h"
#include "protocol.h"
#include "forwarding.h"
#include "neighbor_manager.h"

using namespace Sahayak;

namespace {

uint32_t gNextSequence = 1;
unsigned long gLastHelloMs = 0;
int gLastButtonReading = HIGH;
int gStableButtonState = HIGH;
unsigned long gLastButtonChangeMs = 0;
DuplicateCache gDuplicateCache;
PacketQueue gForwardQueue;
NeighborManager gNeighbors;
NodeState gNodeState = NodeState::DISCOVER_NEIGHBORS;
bool gHasSeenNeighbor = false;

void emitEvent(const char* type, uint8_t origin, uint32_t sequence,
              PacketOutcome outcome, int nextHop = kBroadcastNode,
              uint8_t hop = 0, uint8_t ttl = 0, int rssi = 0,
              float snr = 0.0f, uint8_t queueLength = 0,
              uint8_t retry = 0) {
  Serial.print("EVENT,t_ms=");
  Serial.print(millis());
  Serial.print(",node=");
  Serial.print(SahayakConfig::kNodeId);
  Serial.print(",type=");
  Serial.print(type);
  Serial.print(",origin=");
  Serial.print(origin);
  Serial.print(",seq=");
  Serial.print(sequence);
  Serial.print(",prev=");
  Serial.print(kBroadcastNode);
  Serial.print(",next=");
  Serial.print(nextHop);
  Serial.print(",hop=");
  Serial.print(hop);
  Serial.print(",ttl=");
  Serial.print(ttl);
  Serial.print(",rssi=");
  Serial.print(rssi);
  Serial.print(",snr=");
  Serial.print(snr, 1);
  Serial.print(",queue=");
  Serial.print(queueLength);
  Serial.print(",retry=");
  Serial.print(retry);
  Serial.print(",state=");
  Serial.print(nodeStateName(gNodeState));
  Serial.print(",outcome=");
  Serial.println(outcomeName(outcome));
}

void emitTextEvent(const char* type, PacketOutcome outcome) {
  Serial.print("EVENT,t_ms=");
  Serial.print(millis());
  Serial.print(",node=");
  Serial.print(SahayakConfig::kNodeId);
  Serial.print(",type=");
  Serial.print(type);
  Serial.print(",origin=");
  Serial.print(SahayakConfig::kNodeId);
  Serial.print(",seq=0,prev=255,next=255,hop=0,ttl=0,rssi=0,snr=0,queue=0,retry=0,state=");
  Serial.print(nodeStateName(gNodeState));
  Serial.print(",outcome=");
  Serial.println(outcomeName(outcome));
}

Packet makePacket(MessageType type, uint8_t destination, uint8_t priority,
                  const uint8_t* payload, uint8_t payloadLength) {
  Packet packet{};
  packet.header.version = kProtocolVersion;
  packet.header.messageType = type;
  packet.header.originId = SahayakConfig::kNodeId;
  packet.header.senderId = SahayakConfig::kNodeId;
  packet.header.destinationId = destination;
  packet.header.previousHop = kBroadcastNode;
  packet.header.sequence = gNextSequence++;
  packet.header.routeVersion = 0;
  packet.header.ttl = SahayakConfig::kInitialTtl;
  packet.header.hopCount = 0;
  packet.header.priority = priority;
  packet.header.payloadLength = min(payloadLength, kMaxPayloadBytes);
  packet.header.createdUptimeMs = millis();
  if (packet.header.payloadLength > 0 && payload != nullptr) {
    memcpy(packet.payload, payload, packet.header.payloadLength);
  }
  return packet;
}

bool sendPacket(Packet& packet, uint8_t nextHop) {
  packet.header.senderId = SahayakConfig::kNodeId;

  uint8_t wire[SahayakConfig::kRadioBufferBytes]{};
  size_t wireLength = 0;
  if (!serializePacket(packet, wire, sizeof(wire), wireLength)) {
    emitEvent(messageTypeName(packet.header.messageType), packet.header.originId,
              packet.header.sequence, PacketOutcome::INVALID, nextHop,
              packet.header.hopCount, packet.header.ttl);
    return false;
  }

  // This v0.1 milestone uses direct transmission. The next-hop argument is
  // logged now so the forwarding layer can replace this function later.
  LoRa.idle();
  if (!LoRa.beginPacket()) {
    emitEvent(messageTypeName(packet.header.messageType), packet.header.originId,
              packet.header.sequence, PacketOutcome::NO_ROUTE, nextHop,
              packet.header.hopCount, packet.header.ttl);
    return false;
  }
  LoRa.write(wire, wireLength);
  const int result = LoRa.endPacket();
  LoRa.receive();

  emitEvent(messageTypeName(packet.header.messageType), packet.header.originId,
            packet.header.sequence,
            result == 1 ? PacketOutcome::FORWARDED : PacketOutcome::NO_ROUTE,
            nextHop, packet.header.hopCount, packet.header.ttl);
  return result == 1;
}

void writeU32LittleEndian(uint8_t* out, uint32_t value) {
  out[0] = static_cast<uint8_t>(value & 0xFFu);
  out[1] = static_cast<uint8_t>((value >> 8u) & 0xFFu);
  out[2] = static_cast<uint8_t>((value >> 16u) & 0xFFu);
  out[3] = static_cast<uint8_t>((value >> 24u) & 0xFFu);
}

void refreshNodeState() {
  const uint32_t nowMs = millis();
  gNeighbors.expire(nowMs);
  if (SahayakConfig::kNodeId != SahayakConfig::kBaseStationId &&
      gNeighbors.activeCount(nowMs) == 0 && !gHasSeenNeighbor) {
    gNodeState = NodeState::DISCOVER_NEIGHBORS;
    return;
  }
  gNodeState = routeHealthState(
      gNeighbors, SahayakConfig::kNodeId, SahayakConfig::kBaseStationId,
      SahayakConfig::kStaticNextHop, nowMs);
}

uint8_t advertisedHopCount() {
  if (SahayakConfig::kNodeId == SahayakConfig::kBaseStationId) return 0;
  const uint8_t neighborHop = gNeighbors.advertisedHopFor(
      SahayakConfig::kStaticNextHop, millis());
  if (neighborHop == kUnknownHopCount || neighborHop >= kUnknownHopCount - 1) {
    return kUnknownHopCount;
  }
  return static_cast<uint8_t>(neighborHop + 1);
}

void sendHello() {
  refreshNodeState();
  uint8_t payload[8]{};
  payload[0] = static_cast<uint8_t>(gNodeState);
  payload[1] = 0;  // battery_mV low byte; battery monitor is added later
  payload[2] = 0;  // battery_mV high byte
  payload[3] = static_cast<uint8_t>(gForwardQueue.size());
  payload[4] = advertisedHopCount();
  payload[5] = static_cast<uint8_t>(gNeighbors.activeCount(millis()));
  payload[6] = 0;  // firmware major
  payload[7] = 1;  // firmware minor

  Packet packet = makePacket(MessageType::HELLO, kBroadcastNode, 0, payload,
                             sizeof(payload));
  sendPacket(packet, kBroadcastNode);
}

void sendEmergencyReport() {
  refreshNodeState();
  if (SahayakConfig::kNodeId != SahayakConfig::kBaseStationId &&
      gNodeState == NodeState::ISOLATED) {
    emitTextEvent("REPORT", PacketOutcome::NO_ROUTE);
    return;
  }
  const uint8_t payload[] = {'B', 'U', 'T', 'T', 'O', 'N'};
  Packet packet = makePacket(MessageType::REPORT, SahayakConfig::kBaseStationId,
                             3, payload, sizeof(payload));
  sendPacket(packet, SahayakConfig::kStaticNextHop);
}

void sendAck(const Packet& received) {
  uint8_t payload[7]{};
  payload[0] = received.header.originId;
  writeU32LittleEndian(payload + 1, received.header.sequence);
  payload[5] = 1;  // ACK status: accepted
  payload[6] = SahayakConfig::kNodeId;

  Packet ack = makePacket(MessageType::ACK, received.header.senderId, 3, payload,
                          sizeof(payload));
  ack.header.originId = SahayakConfig::kNodeId;
  ack.header.destinationId = received.header.senderId;
  sendPacket(ack, received.header.senderId);
}

void handleReceivedPacket() {
  const int packetSize = LoRa.parsePacket();
  if (packetSize <= 0) return;

  uint8_t wire[SahayakConfig::kRadioBufferBytes]{};
  size_t length = 0;
  while (LoRa.available() && length < sizeof(wire)) {
    wire[length++] = static_cast<uint8_t>(LoRa.read());
  }
  while (LoRa.available()) LoRa.read();

  Packet packet{};
  if (!deserializePacket(wire, length, packet)) {
    emitTextEvent("UNKNOWN", PacketOutcome::INVALID);
    LoRa.receive();
    return;
  }

  const int rssi = LoRa.packetRssi();
  const float snr = LoRa.packetSnr();
  const int16_t snrX10 = static_cast<int16_t>(snr * 10.0f);

  if (packet.header.messageType == MessageType::HELLO) {
    const bool updated = gNeighbors.updateFromHello(
        packet, static_cast<int16_t>(rssi), snrX10, millis());
    if (updated) gHasSeenNeighbor = true;
    refreshNodeState();
    emitEvent("HELLO", packet.header.originId, packet.header.sequence,
              updated ? PacketOutcome::RECEIVED : PacketOutcome::INVALID,
              packet.header.senderId, packet.header.hopCount, packet.header.ttl,
              rssi, snr, gNeighbors.activeCount(millis()));
    LoRa.receive();
    return;
  }

  refreshNodeState();
  emitEvent(messageTypeName(packet.header.messageType), packet.header.originId,
            packet.header.sequence, PacketOutcome::RECEIVED,
            packet.header.destinationId, packet.header.hopCount, packet.header.ttl,
            rssi, snr, gForwardQueue.size());

  if (packet.header.destinationId != SahayakConfig::kNodeId &&
      packet.header.destinationId != kBroadcastNode) {
    if (packet.header.messageType == MessageType::REPORT) {
      const uint8_t nextHop =
          gNodeState == NodeState::ISOLATED ? kBroadcastNode
                                             : SahayakConfig::kStaticNextHop;
      const ForwardingDecision decision = prepareForward(
          packet, SahayakConfig::kNodeId, nextHop,
          millis(), gDuplicateCache, gForwardQueue);
      emitEvent(messageTypeName(packet.header.messageType), packet.header.originId,
                packet.header.sequence, decision.outcome,
                decision.nextHop, packet.header.hopCount, packet.header.ttl,
                rssi, snr, gForwardQueue.size());
    } else {
      emitEvent(messageTypeName(packet.header.messageType), packet.header.originId,
                packet.header.sequence, PacketOutcome::NO_ROUTE,
                packet.header.destinationId, packet.header.hopCount,
                packet.header.ttl, rssi, snr);
    }
    LoRa.receive();
    return;
  }

  emitEvent(messageTypeName(packet.header.messageType), packet.header.originId,
            packet.header.sequence, PacketOutcome::DELIVERED,
            SahayakConfig::kNodeId, packet.header.hopCount, packet.header.ttl,
            rssi, snr);

  if (packet.header.messageType == MessageType::REPORT) {
    sendAck(packet);
  }
  LoRa.receive();
}

void handleEmergencyButton() {
  const int reading = digitalRead(SahayakConfig::kEmergencyButtonPin);
  if (reading != gLastButtonReading) {
    gLastButtonChangeMs = millis();
    gLastButtonReading = reading;
  }

  if ((millis() - gLastButtonChangeMs) > 40 && reading != gStableButtonState) {
    gStableButtonState = reading;
    if (gStableButtonState == LOW) {
      digitalWrite(SahayakConfig::kRedLedPin, HIGH);
      tone(SahayakConfig::kBuzzerPin, 1800, 150);
      sendEmergencyReport();
    }
  }
}

void flushForwardQueue() {
  if (gForwardQueue.empty()) return;

  QueuedPacket queued{};
  if (!gForwardQueue.dequeue(queued)) return;
  sendPacket(queued.packet, queued.nextHop);
}

void handleSerialCommand() {
  if (!Serial.available()) return;
  const char command = static_cast<char>(Serial.read());
  if (command == 'h' || command == 'H') sendHello();
  if (command == 'r' || command == 'R') sendEmergencyReport();
}

}  // namespace

void setup() {
  Serial.begin(115200);
  delay(300);

  pinMode(SahayakConfig::kEmergencyButtonPin, INPUT_PULLUP);
  pinMode(SahayakConfig::kGreenLedPin, OUTPUT);
  pinMode(SahayakConfig::kRedLedPin, OUTPUT);
  pinMode(SahayakConfig::kBuzzerPin, OUTPUT);
  digitalWrite(SahayakConfig::kGreenLedPin, LOW);
  digitalWrite(SahayakConfig::kRedLedPin, LOW);

  SPI.begin(SahayakConfig::kLoRaSckPin, SahayakConfig::kLoRaMisoPin,
            SahayakConfig::kLoRaMosiPin, SahayakConfig::kLoRaCsPin);
  LoRa.setPins(SahayakConfig::kLoRaCsPin, SahayakConfig::kLoRaResetPin,
               SahayakConfig::kLoRaDio0Pin);

  Serial.println("Sahayak v2.0 firmware booting");
  if (!LoRa.begin(SahayakConfig::kLoRaFrequencyHz)) {
    Serial.println("ERROR,radio_init_failed");
    digitalWrite(SahayakConfig::kRedLedPin, HIGH);
    while (true) delay(1000);
  }

  LoRa.setSignalBandwidth(SahayakConfig::kLoRaBandwidthHz);
  LoRa.setSpreadingFactor(SahayakConfig::kLoRaSpreadingFactor);
  LoRa.setCodingRate4(SahayakConfig::kLoRaCodingRateDenominator);
  LoRa.setTxPower(SahayakConfig::kLoRaTxPowerDbm);
  LoRa.enableCrc();
  LoRa.receive();

  digitalWrite(SahayakConfig::kGreenLedPin, HIGH);
  emitTextEvent("BOOT", PacketOutcome::CREATED);
  sendHello();
  gLastHelloMs = millis();
}

void loop() {
  refreshNodeState();
  handleReceivedPacket();
  flushForwardQueue();
  handleEmergencyButton();
  handleSerialCommand();

  if (millis() - gLastHelloMs >= SahayakConfig::kHelloIntervalMs) {
    sendHello();
    gLastHelloMs = millis();
  }
}
