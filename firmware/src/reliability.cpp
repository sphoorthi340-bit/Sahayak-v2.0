#include "reliability.h"

namespace Sahayak {

ReliabilityManager::ReliabilityManager() : pending_{} {}

bool ReliabilityManager::track(const Packet& packet, uint8_t nextHop,
                               uint32_t nowMs, uint8_t maxRetries) {
  for (size_t i = 0; i < kPendingAckCapacity; ++i) {
    if (!pending_[i].active) {
      pending_[i] = PendingTransmission{
          true, packet, nextHop, 0, maxRetries, nowMs};
      return true;
    }
  }
  return false;
}

bool ReliabilityManager::acknowledge(uint8_t originId, uint32_t sequence) {
  for (size_t i = 0; i < kPendingAckCapacity; ++i) {
    PendingTransmission& item = pending_[i];
    if (!item.active) continue;
    if (item.packet.header.originId == originId &&
        item.packet.header.sequence == sequence) {
      item.active = false;
      return true;
    }
  }
  return false;
}

bool ReliabilityManager::prepareRetry(uint32_t nowMs, uint32_t timeoutMs,
                                      PendingTransmission& output) {
  for (size_t i = 0; i < kPendingAckCapacity; ++i) {
    PendingTransmission& item = pending_[i];
    if (!item.active || static_cast<uint32_t>(nowMs - item.lastSentMs) <
                           timeoutMs) {
      continue;
    }
    if (item.retryCount >= item.maxRetries) continue;
    ++item.retryCount;
    item.lastSentMs = nowMs;
    output = item;
    return true;
  }
  return false;
}

bool ReliabilityManager::expireExhausted(uint32_t nowMs, uint32_t timeoutMs,
                                         PendingTransmission& output) {
  for (size_t i = 0; i < kPendingAckCapacity; ++i) {
    PendingTransmission& item = pending_[i];
    if (!item.active || static_cast<uint32_t>(nowMs - item.lastSentMs) <
                           timeoutMs || item.retryCount < item.maxRetries) {
      continue;
    }
    output = item;
    item.active = false;
    return true;
  }
  return false;
}

size_t ReliabilityManager::activeCount() const {
  size_t count = 0;
  for (const PendingTransmission& item : pending_) {
    if (item.active) ++count;
  }
  return count;
}

}  // namespace Sahayak
