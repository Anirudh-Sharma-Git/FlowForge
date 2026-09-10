# FlowForge

FlowForge is a distributed job and workflow orchestration platform built from scratch in Python.

## Overview

FlowForge allows users to submit individual jobs or DAG-based workflows.

The platform is responsible for:

- persisting execution state
- scheduling work
- assigning work to workers
- tracking worker health
- recovering failed work
- retrying failed jobs
- preventing duplicate state transitions
- executing dependent workflows
- publishing lifecycle events
- exposing execution state and metrics

## Architecture

```text
Client
   |
   v
FastAPI Control Plane
   |
   +-------------------+
   |                   |
   v                   v
PostgreSQL           Redis
   |
   v
Scheduler
   |
   v
Workers
   |
   v
Kafka
   |
   v
Consumers