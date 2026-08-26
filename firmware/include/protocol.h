#pragma once

#include <Arduino.h>
#include <stdint.h>

namespace Sahayak {

constexpr uint8_t kProtocolVersion = 1;
constexpr uint8_t kBroadcastNode = 255;
constexpr uint8_t kBaseStationId = 1;
constexpr uint8_t kMaxPayloadBytes = 80;
constexpr uint8_t kDefaultTtl = 8;

// Values are part of the wire protocol. Do not reorder existing values.
enum class MessageType : uint8_t {
  HELLO = 1,
  REPORT = 2,
  ACK = 3,
  STATUS = 4,
  ROUTE_UPDATE = 5,
  FAILURE_RISK = 6,
  COMMAND = 7,
};

enum class NodeState : uint8_t {
  BOOT = 0,
  SELF_TEST = 1,
  DISCOVER_NEIGHBORS = 2,
  CONNECTED = 3,
  DEGRADED = 4,
  AT_RISK = 5,
  TRANSMITTING = 6,
  WAITING_ACK = 7,
  RETRYING = 8,
  ISOLATED = 9,
};

enum class PacketOutcome : uint8_t {
  CREATED = 0,
  RECEIVED = 1,
  DELIVERED = 2,
  ACKED = 3,
  QUEUED = 4,
  FORWARDED = 5,
  DUPLICATE = 6,
  INVALID = 7,
  NO_ROUTE = 8,
  TTL_EXPIRED = 9,
  RETRY_LIMIT_REACHED = 10,
  ROUTE_LOOP = 11,
  QUEUE_FULL = 12,
};

// Version 0.1 header. Serialization is deliberately kept in packet.cpp so
// wire layout is explicit instead of relying on compiler struct packing.
struct PacketHeader {
  uint8_t version;
  MessageType messageType;
  uint8_t originId;
  uint8_t senderId;
  uint8_t destinationId;
  uint8_t previousHop;
  uint32_t sequence;
  uint16_t routeVersion;
  uint8_t ttl;
  uint8_t hopCount;
  uint8_t priority;
  uint8_t payloadLength;
  uint32_t createdUptimeMs;
};

struct Packet {
  PacketHeader header{};
  uint8_t payload[kMaxPayloadBytes]{};
};

struct HelloPayload {
  NodeState nodeState;
  uint16_t batteryMv;
  uint8_t queueLength;
  uint8_t advertisedHopCount;
  uint8_t neighborCount;
  uint8_t firmwareMajor;
  uint8_t firmwareMinor;
};

struct AckPayload {
  uint8_t acknowledgedOriginId;
  uint32_t acknowledgedSequence;
  uint8_t ackStatus;
  uint8_t ackSenderId;
};

const char* messageTypeName(MessageType type);
const char* nodeStateName(NodeState state);
const char* outcomeName(PacketOutcome outcome);

bool serializePacket(const Packet& packet, uint8_t* output, size_t capacity,
                    size_t& outputLength);
bool deserializePacket(const uint8_t* input, size_t inputLength,
                       Packet& packet);

}  // namespace Sahayak
