#!/bin/bash
#bash script for sending SMS with gammu daemon
echo $1 | sudo gammu-smsd-inject TEXT $2