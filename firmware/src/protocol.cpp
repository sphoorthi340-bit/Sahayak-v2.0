#include "protocol.h"

#include <string.h>

namespace Sahayak {
namespace {

constexpr size_t kWireHeaderBytes = 20;

void writeU16(uint8_t* output, size_t& offset, uint16_t value) {
  output[offset++] = static_cast<uint8_t>(value & 0xFFu);
  output[offset++] = static_cast<uint8_t>((value >> 8u) & 0xFFu);
}

void writeU32(uint8_t* output, size_t& offset, uint32_t value) {
  output[offset++] = static_cast<uint8_t>(value & 0xFFu);
  output[offset++] = static_cast<uint8_t>((value >> 8u) & 0xFFu);
  output[offset++] = static_cast<uint8_t>((value >> 16u) & 0xFFu);
  output[offset++] = static_cast<uint8_t>((value >> 24u) & 0xFFu);
}

bool readU16(const uint8_t* input, size_t inputLength, size_t& offset,
             uint16_t& value) {
  if (offset + 2 > inputLength) return false;
  value = static_cast<uint16_t>(input[offset]) |
          (static_cast<uint16_t>(input[offset + 1]) << 8u);
  offset += 2;
  return true;
}

bool readU32(const uint8_t* input, size_t inputLength, size_t& offset,
             uint32_t& value) {
  if (offset + 4 > inputLength) return false;
  value = static_cast<uint32_t>(input[offset]) |
          (static_cast<uint32_t>(input[offset + 1]) << 8u) |
          (static_cast<uint32_t>(input[offset + 2]) << 16u) |
          (static_cast<uint32_t>(input[offset + 3]) << 24u);
  offset += 4;
  return true;
}

}  // namespace

const char* messageTypeName(MessageType type) {
  switch (type) {
    case MessageType::HELLO: return "HELLO";
    case MessageType::REPORT: return "REPORT";
    case MessageType::ACK: return "ACK";
    case MessageType::STATUS: return "STATUS";
    case MessageType::ROUTE_UPDATE: return "ROUTE_UPDATE";
    case MessageType::FAILURE_RISK: return "FAILURE_RISK";
    case MessageType::COMMAND: return "COMMAND";
    default: return "UNKNOWN";
  }
}

const char* nodeStateName(NodeState state) {
  switch (state) {
    case NodeState::BOOT: return "BOOT";
    case NodeState::SELF_TEST: return "SELF_TEST";
    case NodeState::DISCOVER_NEIGHBORS: return "DISCOVER_NEIGHBORS";
    case NodeState::CONNECTED: return "CONNECTED";
    case NodeState::DEGRADED: return "DEGRADED";
    case NodeState::AT_RISK: return "AT_RISK";
    case NodeState::TRANSMITTING: return "TRANSMITTING";
    case NodeState::WAITING_ACK: return "WAITING_ACK";
    case NodeState::RETRYING: return "RETRYING";
    case NodeState::ISOLATED: return "ISOLATED";
    default: return "UNKNOWN";
  }
}

const char* outcomeName(PacketOutcome outcome) {
  switch (outcome) {
    case PacketOutcome::CREATED: return "CREATED";
    case PacketOutcome::RECEIVED: return "RECEIVED";
    case PacketOutcome::DELIVERED: return "DELIVERED";
    case PacketOutcome::ACKED: return "ACKED";
    case PacketOutcome::QUEUED: return "QUEUED";
    case PacketOutcome::FORWARDED: return "FORWARDED";
    case PacketOutcome::DUPLICATE: return "DUPLICATE";
    case PacketOutcome::INVALID: return "INVALID";
    case PacketOutcome::NO_ROUTE: return "NO_ROUTE";
    case PacketOutcome::TTL_EXPIRED: return "TTL_EXPIRED";
    case PacketOutcome::RETRY_LIMIT_REACHED: return "RETRY_LIMIT_REACHED";
    case PacketOutcome::ROUTE_LOOP: return "ROUTE_LOOP";
    case PacketOutcome::QUEUE_FULL: return "QUEUE_FULL";
    default: return "UNKNOWN";
  }
}

bool serializePacket(const Packet& packet, uint8_t* output, size_t capacity,
                    size_t& outputLength) {
  outputLength = 0;
  if (output == nullptr || packet.header.payloadLength > kMaxPayloadBytes) {
    return false;
  }

  const size_t required = kWireHeaderBytes + packet.header.payloadLength;
  if (capacity < required) return false;

  size_t offset = 0;
  output[offset++] = packet.header.version;
  output[offset++] = static_cast<uint8_t>(packet.header.messageType);
  output[offset++] = packet.header.originId;
  output[offset++] = packet.header.senderId;
  output[offset++] = packet.header.destinationId;
  output[offset++] = packet.header.previousHop;
  writeU32(output, offset, packet.header.sequence);
  writeU16(output, offset, packet.header.routeVersion);
  output[offset++] = packet.header.ttl;
  output[offset++] = packet.header.hopCount;
  output[offset++] = packet.header.priority;
  output[offset++] = packet.header.payloadLength;
  writeU32(output, offset, packet.header.createdUptimeMs);

  if (packet.header.payloadLength > 0) {
    memcpy(output + offset, packet.payload, packet.header.payloadLength);
    offset += packet.header.payloadLength;
  }

  outputLength = offset;
  return true;
}

bool deserializePacket(const uint8_t* input, size_t inputLength,
                       Packet& packet) {
  if (input == nullptr || inputLength < kWireHeaderBytes) return false;

  size_t offset = 0;
  PacketHeader header{};
  header.version = input[offset++];
  header.messageType = static_cast<MessageType>(input[offset++]);
  header.originId = input[offset++];
  header.senderId = input[offset++];
  header.destinationId = input[offset++];
  header.previousHop = input[offset++];

  if (!readU32(input, inputLength, offset, header.sequence)) return false;
  if (!readU16(input, inputLength, offset, header.routeVersion)) return false;

  header.ttl = input[offset++];
  header.hopCount = input[offset++];
  header.priority = input[offset++];
  header.payloadLength = input[offset++];
  if (!readU32(input, inputLength, offset, header.createdUptimeMs)) return false;

  if (header.version != kProtocolVersion ||
      header.payloadLength > kMaxPayloadBytes ||
      inputLength != kWireHeaderBytes + header.payloadLength) {
    return false;
  }

  packet = Packet{};
  packet.header = header;
  if (header.payloadLength > 0) {
    memcpy(packet.payload, input + offset, header.payloadLength);
  }
  return true;
}

}  // namespace Sahayak
