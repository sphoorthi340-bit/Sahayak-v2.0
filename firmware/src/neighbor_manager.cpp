#include "neighbor_manager.h"

namespace Sahayak {
namespace {

uint16_t readU16LittleEndian(const uint8_t* input) {
  return static_cast<uint16_t>(input[0]) |
         (static_cast<uint16_t>(input[1]) << 8u);
}

bool isNeighborStateHealthy(NodeState state) {
  return state == NodeState::CONNECTED ||
         state == NodeState::DISCOVER_NEIGHBORS ||
         state == NodeState::DEGRADED;
}

}  // namespace

NeighborManager::NeighborManager() : records_{} {}

NeighborRecord* NeighborManager::findMutable(uint8_t nodeId) {
  for (size_t i = 0; i < kNeighborTableCapacity; ++i) {
    if (records_[i].valid && records_[i].nodeId == nodeId) return &records_[i];
  }
  return nullptr;
}

NeighborRecord* NeighborManager::allocate(uint8_t nodeId, uint32_t nowMs) {
  NeighborRecord* oldest = &records_[0];
  uint32_t oldestAge = 0;
  for (size_t i = 0; i < kNeighborTableCapacity; ++i) {
    if (!records_[i].valid) return &records_[i];
    const uint32_t age = static_cast<uint32_t>(nowMs - records_[i].lastHeardMs);
    if (age >= oldestAge) {
      oldestAge = age;
      oldest = &records_[i];
    }
  }
  (void)nodeId;
  return oldest;
}

bool NeighborManager::updateFromHello(const Packet& packet, int16_t rssiDbm,
                                      int16_t snrX10, uint32_t nowMs) {
  if (packet.header.messageType != MessageType::HELLO ||
      packet.header.payloadLength < 8 ||
      packet.header.senderId == kBroadcastNode) {
    return false;
  }

  NeighborRecord* record = findMutable(packet.header.senderId);
  if (record == nullptr) record = allocate(packet.header.senderId, nowMs);
  if (record == nullptr) return false;

  record->valid = true;
  record->nodeId = packet.header.senderId;
  record->nodeState = static_cast<NodeState>(packet.payload[0]);
  record->batteryMv = readU16LittleEndian(packet.payload + 1);
  record->queueLength = packet.payload[3];
  record->advertisedHopCount = packet.payload[4];
  record->neighborCount = packet.payload[5];
  record->firmwareMajor = packet.payload[6];
  record->firmwareMinor = packet.payload[7];
  record->lastRssiDbm = rssiDbm;
  record->lastSnrX10 = snrX10;
  record->lastHeardMs = nowMs;
  return true;
}

size_t NeighborManager::expire(uint32_t nowMs) {
  size_t expired = 0;
  for (size_t i = 0; i < kNeighborTableCapacity; ++i) {
    if (!records_[i].valid) continue;
    if (static_cast<uint32_t>(nowMs - records_[i].lastHeardMs) >
        kNeighborExpiryMs) {
      records_[i].valid = false;
      ++expired;
    }
  }
  return expired;
}

bool NeighborManager::isFresh(uint8_t nodeId, uint32_t nowMs) const {
  const NeighborRecord* record = find(nodeId, nowMs);
  return record != nullptr;
}

const NeighborRecord* NeighborManager::find(uint8_t nodeId,
                                            uint32_t nowMs) const {
  for (size_t i = 0; i < kNeighborTableCapacity; ++i) {
    const NeighborRecord& record = records_[i];
    if (!record.valid || record.nodeId != nodeId) continue;
    if (static_cast<uint32_t>(nowMs - record.lastHeardMs) >
        kNeighborExpiryMs) {
      return nullptr;
    }
    return &record;
  }
  return nullptr;
}

size_t NeighborManager::activeCount(uint32_t nowMs) const {
  size_t count = 0;
  for (size_t i = 0; i < kNeighborTableCapacity; ++i) {
    if (records_[i].valid &&
        static_cast<uint32_t>(nowMs - records_[i].lastHeardMs) <=
            kNeighborExpiryMs) {
      ++count;
    }
  }
  return count;
}

uint8_t NeighborManager::advertisedHopFor(uint8_t nodeId,
                                          uint32_t nowMs) const {
  const NeighborRecord* record = find(nodeId, nowMs);
  return record == nullptr ? kUnknownHopCount : record->advertisedHopCount;
}

uint8_t NeighborManager::queueLengthFor(uint8_t nodeId, uint32_t nowMs) const {
  const NeighborRecord* record = find(nodeId, nowMs);
  return record == nullptr ? 255 : record->queueLength;
}

NodeState routeHealthState(const NeighborManager& neighbors, uint8_t localId,
                           uint8_t baseStationId, uint8_t staticNextHop,
                           uint32_t nowMs) {
  if (localId == baseStationId) return NodeState::CONNECTED;

  const NeighborRecord* next = neighbors.find(staticNextHop, nowMs);
  if (next == nullptr) return NodeState::ISOLATED;
  if (!isNeighborStateHealthy(next->nodeState)) return NodeState::AT_RISK;
  if (next->advertisedHopCount == kUnknownHopCount ||
      next->nodeState == NodeState::DEGRADED) {
    return NodeState::DEGRADED;
  }
  return NodeState::CONNECTED;
}

}  // namespace Sahayak
