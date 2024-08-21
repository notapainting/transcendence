#!/bin/bash
daphne -b 0.0.0.0 -p 8000 game_back.asgi:application
