#pragma once

#include <stddef.h>
#include <stdint.h>

#include "protocol.h"

namespace Sahayak {

constexpr size_t kNeighborTableCapacity = 16;
constexpr uint32_t kNeighborExpiryMs = 30000UL;
constexpr uint8_t kUnknownHopCount = 255;

struct NeighborRecord {
  bool valid;
  uint8_t nodeId;
  NodeState nodeState;
  uint16_t batteryMv;
  uint8_t queueLength;
  uint8_t advertisedHopCount;
  uint8_t neighborCount;
  uint8_t firmwareMajor;
  uint8_t firmwareMinor;
  int16_t lastRssiDbm;
  int16_t lastSnrX10;
  uint32_t lastHeardMs;
};

struct RoutingWeights {
  uint8_t rssi;
  uint8_t hop;
  uint8_t queue;
};

constexpr RoutingWeights kDefaultRoutingWeights{50, 25, 25};

class NeighborManager {
 public:
  NeighborManager();

  bool updateFromHello(const Packet& packet, int16_t rssiDbm, int16_t snrX10,
                       uint32_t nowMs);
  size_t expire(uint32_t nowMs);
  bool isFresh(uint8_t nodeId, uint32_t nowMs) const;
  const NeighborRecord* find(uint8_t nodeId, uint32_t nowMs) const;
  size_t activeCount(uint32_t nowMs) const;
  uint8_t advertisedHopFor(uint8_t nodeId, uint32_t nowMs) const;
  uint8_t queueLengthFor(uint8_t nodeId, uint32_t nowMs) const;
  uint8_t selectNextHop(uint8_t localId, uint8_t previousHop,
                        uint32_t nowMs,
                        RoutingWeights weights = kDefaultRoutingWeights) const;

 private:
  NeighborRecord records_[kNeighborTableCapacity];

  NeighborRecord* findMutable(uint8_t nodeId);
  NeighborRecord* allocate(uint8_t nodeId, uint32_t nowMs);
};

NodeState routeHealthState(const NeighborManager& neighbors, uint8_t localId,
                           uint8_t baseStationId, uint8_t staticNextHop,
                           uint32_t nowMs);

NodeState dynamicRouteHealthState(const NeighborManager& neighbors,
                                  uint8_t localId, uint8_t baseStationId,
                                  uint8_t previousHop, uint32_t nowMs,
                                  RoutingWeights weights = kDefaultRoutingWeights);

}  // namespace Sahayak
