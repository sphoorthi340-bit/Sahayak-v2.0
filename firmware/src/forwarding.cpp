#include "forwarding.h"

namespace Sahayak {

DuplicateCache::DuplicateCache() : entries_{} {}

bool DuplicateCache::contains(uint8_t originId, uint32_t sequence,
                              uint32_t nowMs) {
  for (size_t i = 0; i < kDuplicateCacheCapacity; ++i) {
    Entry& entry = entries_[i];
    if (!entry.valid) continue;
    if (static_cast<uint32_t>(nowMs - entry.seenMs) > kDuplicateExpiryMs) {
      entry.valid = false;
      continue;
    }
    if (entry.originId == originId && entry.sequence == sequence) return true;
  }
  return false;
}

void DuplicateCache::remember(uint8_t originId, uint32_t sequence,
                              uint32_t nowMs) {
  size_t freeIndex = kDuplicateCacheCapacity;
  size_t oldestIndex = 0;
  uint32_t oldestAge = 0;

  for (size_t i = 0; i < kDuplicateCacheCapacity; ++i) {
    Entry& entry = entries_[i];
    if (entry.valid && entry.originId == originId &&
        entry.sequence == sequence) {
      entry.seenMs = nowMs;
      return;
    }
    if (!entry.valid && freeIndex == kDuplicateCacheCapacity) {
      freeIndex = i;
    }
    if (entry.valid) {
      const uint32_t age = static_cast<uint32_t>(nowMs - entry.seenMs);
      if (age >= oldestAge) {
        oldestAge = age;
        oldestIndex = i;
      }
    }
  }

  const size_t index = freeIndex < kDuplicateCacheCapacity ? freeIndex
                                                             : oldestIndex;
  entries_[index] = Entry{true, originId, sequence, nowMs};
}

PacketQueue::PacketQueue() : items_{}, count_(0), insertionCounter_(0) {}

bool PacketQueue::enqueue(const Packet& packet, uint8_t nextHop,
                          uint32_t nowMs) {
  if (count_ >= kForwardQueueCapacity) return false;

  size_t position = count_;
  while (position > 0 &&
         items_[position - 1].packet.header.priority < packet.header.priority) {
    items_[position] = items_[position - 1];
    --position;
  }

  items_[position] = QueuedPacket{packet, nextHop, nowMs};
  ++count_;
  ++insertionCounter_;
  return true;
}

bool PacketQueue::dequeue(QueuedPacket& output) {
  if (count_ == 0) return false;
  output = items_[0];
  for (size_t i = 1; i < count_; ++i) items_[i - 1] = items_[i];
  --count_;
  return true;
}

size_t PacketQueue::size() const { return count_; }

bool PacketQueue::empty() const { return count_ == 0; }

ForwardingDecision prepareForward(const Packet& received, uint8_t localId,
                                  uint8_t nextHop, uint32_t nowMs,
                                  DuplicateCache& duplicates,
                                  PacketQueue& queue) {
  if (duplicates.contains(received.header.originId,
                           received.header.sequence, nowMs)) {
    return {ForwardAction::DROP, PacketOutcome::DUPLICATE, nextHop};
  }
  duplicates.remember(received.header.originId, received.header.sequence,
                      nowMs);

  if (received.header.ttl == 0) {
    return {ForwardAction::DROP, PacketOutcome::TTL_EXPIRED, nextHop};
  }
  if (received.header.destinationId == localId) {
    return {ForwardAction::DELIVER, PacketOutcome::DELIVERED, localId};
  }
  if (nextHop == localId || nextHop == received.header.previousHop ||
      nextHop == kBroadcastNode) {
    return {ForwardAction::DROP, PacketOutcome::ROUTE_LOOP, nextHop};
  }

  Packet forwarded = received;
  forwarded.header.senderId = localId;
  forwarded.header.previousHop = received.header.senderId;
  --forwarded.header.ttl;
  ++forwarded.header.hopCount;

  if (!queue.enqueue(forwarded, nextHop, nowMs)) {
    return {ForwardAction::DROP, PacketOutcome::QUEUE_FULL, nextHop};
  }
  return {ForwardAction::QUEUE, PacketOutcome::QUEUED, nextHop};
}

}  // namespace Sahayak
