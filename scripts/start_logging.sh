#!/bin/bash

log_subscriber --channel ModuleManager --log_path ~/gits/bgp-ranking/logs/ &
log_subscriber --channel FetchRawFiles --log_path ~/gits/bgp-ranking/logs/ &
log_subscriber --channel ParseRawFiles --log_path ~/gits/bgp-ranking/logs/ &
log_subscriber --channel DatabaseInput --log_path ~/gits/bgp-ranking/logs/ &
log_subscriber --channel RISWhoisInsert --log_path ~/gits/bgp-ranking/logs/ &
log_subscriber --channel RISWhoisFetch --log_path ~/gits/bgp-ranking/logs/ &
