# MCP Chat Documentation

Welcome to the MCP Chat server documentation. This directory contains all documentation organized by category.

## 📋 Planning

Documents related to project planning and design:

- [**Project Overview**](planning/overview.md) - High-level project summary and key decisions
- [**MVP Plan**](planning/mvp-plan.md) - Simplified first version focusing on core features
- [**Implementation Plan**](planning/implementation-plan.md) - Detailed architecture and development phases
- [**Terminal Client Plan**](planning/terminal-client-plan.md) - Design for Textual-based terminal UI client
- [**Long-Polling Design**](planning/long-polling-design.md) - Alternative approach using blocking tool calls

## 🛠️ Implementation

Technical implementation details:

- [**Technical Decisions**](implementation/technical-decisions.md) - Key architectural choices and rationale

## 📖 Usage

Guides for running and testing the server:

- [**Quick Test Guide**](usage/quick-test.md) - Fastest way to test the server
- [**Running the Server**](usage/running-server.md) - Detailed server startup and configuration
- [**Testing Guide**](usage/testing-guide.md) - Comprehensive testing strategies and examples

## 🔧 Technical Reference

Deep technical documentation:

- [**Communication Patterns**](technical/communication-patterns.md) - FastMCP communication features explained
- [**Notifications Guide**](technical/notifications-guide.md) - MCP notifications implementation details

## Quick Links

### Getting Started
1. Read the [Project Overview](planning/overview.md)
2. Follow the [Running the Server](usage/running-server.md) guide
3. Test with the [Quick Test Guide](usage/quick-test.md)

### For Developers
1. Review [Technical Decisions](implementation/technical-decisions.md)
2. Understand [Communication Patterns](technical/communication-patterns.md)
3. Check the [Implementation Plan](planning/implementation-plan.md)

### Current Status
- ✅ Basic server implementation complete
- ✅ In-memory queue and room management
- ✅ Three core tools: enter_queue, send_message, leave_chat
- ⚠️ Connection tracking needs implementation
- 🔄 Considering long-polling approach for universal client compatibility