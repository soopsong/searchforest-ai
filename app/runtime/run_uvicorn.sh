#!/bin/bash

uvicorn runtime.api:app --host 0.0.0.0 --port 8004 --reload
