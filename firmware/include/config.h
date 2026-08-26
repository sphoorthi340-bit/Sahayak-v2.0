#pragma once

#include <Arduino.h>

namespace SahayakConfig {

// Change this per node before flashing. Node 1 is the base station.
constexpr uint8_t kNodeId = 2;
constexpr uint8_t kBaseStationId = 1;

// First three-node milestone only. Set this per flashed node, for example:
// field node -> relay, relay -> base station. Dynamic routing replaces this.
constexpr uint8_t kStaticNextHop = 1;

// Dynamic routing weights are normalized internally; these values need not sum
// to a specific number. Keep them configurable for controlled experiments.
constexpr uint8_t kRssiWeight = 50;
constexpr uint8_t kHopWeight = 25;
constexpr uint8_t kQueueWeight = 25;
constexpr int16_t kRouteHysteresisPoints = 5;

// Confirm these against the purchased radio module and local operating rules.
// Provisional in-band test frequency; confirm the permitted channel before RF testing.
constexpr long kLoRaFrequencyHz = 866500000L;
constexpr long kLoRaBandwidthHz = 125000L;
constexpr uint8_t kLoRaSpreadingFactor = 7;
constexpr uint8_t kLoRaCodingRateDenominator = 5;
// Keep this conservative until the module, antenna, and local RF limits are confirmed.
constexpr int8_t kLoRaTxPowerDbm = 14;

// Example SPI and radio-control pins for a standard ESP32 DevKit.
constexpr int kLoRaCsPin = 5;
constexpr int kLoRaResetPin = 14;
constexpr int kLoRaDio0Pin = 26;
constexpr int kLoRaSckPin = 18;
constexpr int kLoRaMisoPin = 19;
constexpr int kLoRaMosiPin = 23;

// Example I2C/UI pins. OLED and UI modules are integrated in a later milestone.
constexpr int kOledSdaPin = 21;
constexpr int kOledSclPin = 22;
constexpr int kEmergencyButtonPin = 27;
constexpr int kGreenLedPin = 25;
constexpr int kRedLedPin = 32;
constexpr int kBuzzerPin = 13;

constexpr unsigned long kHelloIntervalMs = 10000UL;
constexpr unsigned long kAckTimeoutMs = 2500UL;
constexpr uint8_t kMaxRetries = 3;
constexpr uint8_t kInitialTtl = 8;
constexpr size_t kRadioBufferBytes = 128;

}  // namespace SahayakConfig
