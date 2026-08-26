#pragma once

#include <Arduino.h>
#include <stddef.h>
#include <stdint.h>

#include "protocol.h"

namespace Sahayak {

constexpr size_t kForwardQueueCapacity = 8;
constexpr size_t kDuplicateCacheCapacity = 32;
constexpr uint32_t kDuplicateExpiryMs = 120000UL;

enum class ForwardAction : uint8_t {
  DELIVER = 0,
  QUEUE = 1,
  DROP = 2,
};

struct ForwardingDecision {
  ForwardAction action;
  PacketOutcome outcome;
  uint8_t nextHop;
};

class DuplicateCache {
 public:
  DuplicateCache();
  bool contains(uint8_t originId, uint32_t sequence, uint32_t nowMs);
  void remember(uint8_t originId, uint32_t sequence, uint32_t nowMs);

 private:
  struct Entry {
    bool valid;
    uint8_t originId;
    uint32_t sequence;
    uint32_t seenMs;
  };

  Entry entries_[kDuplicateCacheCapacity];
};

struct QueuedPacket {
  Packet packet;
  uint8_t nextHop;
  uint32_t enqueuedMs;
};

class PacketQueue {
 public:
  PacketQueue();
  bool enqueue(const Packet& packet, uint8_t nextHop, uint32_t nowMs);
  bool dequeue(QueuedPacket& output);
  size_t size() const;
  bool empty() const;

 private:
  QueuedPacket items_[kForwardQueueCapacity];
  size_t count_;
  uint32_t insertionCounter_;
};

ForwardingDecision prepareForward(const Packet& received, uint8_t localId,
                                  uint8_t nextHop, uint32_t nowMs,
                                  DuplicateCache& duplicates,
                                  PacketQueue& queue);

}  // namespace Sahayak
