#pragma once

#include <stddef.h>
#include <stdint.h>

#include "protocol.h"

namespace Sahayak {

constexpr size_t kPendingAckCapacity = 8;

struct PendingTransmission {
  bool active;
  Packet packet;
  uint8_t nextHop;
  uint8_t retryCount;
  uint8_t maxRetries;
  uint32_t lastSentMs;
};

class ReliabilityManager {
 public:
  ReliabilityManager();

  bool track(const Packet& packet, uint8_t nextHop, uint32_t nowMs,
             uint8_t maxRetries);
  bool acknowledge(uint8_t originId, uint32_t sequence);
  bool prepareRetry(uint32_t nowMs, uint32_t timeoutMs,
                    PendingTransmission& output);
  bool expireExhausted(uint32_t nowMs, uint32_t timeoutMs,
                       PendingTransmission& output);
  size_t activeCount() const;

 private:
  PendingTransmission pending_[kPendingAckCapacity];
};

}  // namespace Sahayak
