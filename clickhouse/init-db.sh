#!/bin/bash
set -e

clickhouse client -n <<-EOSQL
    CREATE DATABASE IF NOT EXISTS real_data;
    CREATE TABLE IF NOT EXISTS real_data.localization (id String, timestamp DateTime('Europe/Warsaw'), lon Float32, lat Float32) ENGINE = TinyLog;
EOSQL