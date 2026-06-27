# Nexus Security Auditor - User Guide

## Overview

Nexus Security Auditor adalah framework audit keamanan defensif untuk melakukan pemeriksaan konfigurasi dan informasi sistem secara lokal.

## Instalasi

pip install -r requirements.txt

## Menjalankan Audit

python3 main.py audit

## Melihat Versi

python3 main.py version

## Melihat Modul

python3 main.py list-modules

## Output

# Hasil audit tersedia pada:

reports/report.json

reports/report.html

# Log aktivitas tersedia pada:

logs/nexus.log

## Modul Audit

System Audit

Service Audit

Network Audit

Process Audit

User Audit

Filesystem Audit

File Permission Audit

Password Policy Audit

Patch Audit


## Prinsip Keamanan

# Tool ini dibuat untuk:

audit defensif

hardening sistem

pemeriksaan konfigurasi

pembelajaran keamanan


# Gunakan hanya pada sistem yang memiliki izin audit #
