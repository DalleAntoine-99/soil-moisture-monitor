# 📋 Plant IoT Monitor - TODO List (VM Architecture)

--- 4B.52
Questions: 
- Est-ce qu'on peut avoir un répertoire partagé sur la VM. (Même utilisateur Ubuntu) TP-Hadoop-12 

- Créer Git Hub @antoine
- Créer la sortie cible Factice VM image, percentage humidité, label de classification (échelle de 3) @antoine
- Thnigboard code qui envoie les 3 élements d'une VM à notre thingsboard @Guy
- Est-ce qu'on peut avoir un répertoire partagé sur la VM. (Même utilisateur Ubuntu) TP-Hadoop-12 @Guy @antoine













## ✅ SETUP & ENVIRONMENT

### Git & Repository @Antoine
**Done when:** Repository created, both devs can clone and push
- [ ] Create GitHub repository
- [ ] Add collaborator with write access
- [ ] Create `.gitignore` (Python, venv, models, secrets)
- [ ] Initial commit with project structure

### Development Environment - Local Machines
**Done when:** Both Mac and Linux can capture images successfully @Guy @Antoine
- [ ] **Mac**: Install Python 3.10+, create venv, test camera
- [ ] **Linux**: Install Python 3.10+, create venv, test camera
- [ ] Install capture dependencies (OpenCV/PIL)
- [ ] Verify image capture works on both OS

### Development Environment - VM
**Done when:** VM can run ML inference and connect to ThingsBoard
- [ ] Provision VM (cloud provider or local VirtualBox)
- [ ] Install Python 3.10+ on VM
- [ ] Install PyTorch + dependencies on VM
- [ ] Test model loading on VM
- [ ] Configure network access (SSH, MQTT port 1883)
- [ ] Setup firewall rules (allow inbound image upload)

### ThingsBoard Account @Guy 
**Done when:** Can publish test MQTT message and see it in dashboard
- [ ] Create account on demo.thingsboard.io
- [ ] Create Device (for VM)
- [ ] Save access token securely
- [ ] Test MQTT connection from VM

### ThingsBoard Cloud to install @Guy
**Done when:** A cloud Thingboard is running properly
- [ ] XXX

---

## 📸 CAPTURE MODULE (Local Machines)

### Linux Capture
**Done when:** Can capture image every 2 minutes (to modify) automatically and save locally @Guy
- [ ] Create `LinuxCapture` class
- [ ] Add error handling (camera unavailable, retry logic)
- [ ] Test with different camera indices (0, 1)
- [ ] Add timestamp to filenames
- [ ] Write unit tests with mock camera

### Mac Capture  
**Done when:** Can capture image every 2h automatically and save locally @Antoine
- [ ] Create `MacCapture` class
- [ ] Handle macOS camera permissions
- [ ] Test with FaceTime camera
- [ ] Add error handling and retry logic
- [ ] Write unit tests with mock camera

### Capture Abstraction P2
**Done when:** Same code runs on Mac and Linux, auto-detects OS
- [ ] Create `base.py` with `CaptureInterface`
- [ ] Implement OS auto-detection
- [ ] Test factory pattern works on both systems
- [ ] Document interface usage

---

## 📤 IMAGE UPLOAD TO VM

### Upload Client (Local Machines)
**Done when:** Images successfully transferred to VM after capture 
- [ ] Create `upload_client.py` module
- [ ] Implement file upload (SCP/SFTP or HTTP POST)
- [ ] Add authentication (SSH keys or API token)
- [ ] Handle upload failures (retry with exponential backoff)
- [ ] Add upload queue for offline mode
- [ ] Verify file integrity after upload (checksum)

### Upload Server (VM)
**Done when:** VM receives images and stores them securely
- [ ] Create REST API endpoint (Flask/FastAPI) OR configure SSH/FTP server
- [ ] Implement file reception and validation
- [ ] Store images in `/data/incoming/` directory
- [ ] Add access control (authentication required)
- [ ] Log all uploads with timestamps
- [ ] Auto-cleanup old images (retention policy)

---

## 🧠 MACHINE LEARNING MODULE (VM Only)

### Model Setup
**Done when:** Model loads successfully on VM and produces predictions
- [ ] Upload best_model.pt to VM
- [ ] Test model loading (handle CPU-only if no GPU)
- [ ] Verify model architecture matches training
- [ ] Benchmark inference time on VM hardware

### Inference Pipeline (VM)
**Done when:** VM automatically processes new images and outputs predictions
- [ ] Create `inference.py` module
- [ ] Implement preprocessing (resize, crop, normalize)
- [ ] Implement inference function
- [ ] Extract confidence scores and class predictions
- [ ] Add error handling (corrupted images, OOM)
- [ ] Write unit tests with sample images
- [ ] Optimize for VM resources (memory, CPU)

### File Watcher (VM)
**Done when:** VM detects new images automatically and triggers inference. Vérifier ou utiliser un endpoint pour recevoir les images, et lorsqu'il recoit l'image (END POINT, pour ne pas vérifier un repertoire) 
- [ ] Create file watcher (watchdog library or inotify)
- [ ] Monitor `/data/incoming/` directory
- [ ] Trigger inference on new file
- [ ] Move processed images to `/data/processed/`
- [ ] Handle concurrent uploads gracefully

---

## 💾 STORAGE MODULE (VM Only)

### SQLite Database (VM)
**Done when:** VM stores all inference results queryable by timestamp (Une stratégie de stockage, est-ce qu'on peut stocke sur mongoDB ? à investiguer ?)
- [ ] Design database schema (timestamp, image_path, prediction, confidence)
- [ ] Create `storage.py` module
- [ ] Implement table creation and CRUD operations
- [ ] Add indexing on timestamp
- [ ] Implement data retention policy (auto-delete old records)
- [ ] Write unit tests

### Backup & Sync
**Done when:** No data loss even if VM crashes (P2)
- [ ] Implement local backup (periodic DB dump)
- [ ] Add flag `uploaded_to_cloud` in DB
- [ ] Implement retry mechanism for failed MQTT publishes

---

## 📡 MQTT COMMUNICATION (VM to ThingsBoard)

### MQTT Client (VM) (Protocole to send Data ThingsBoard - We can do HTTP if you get trouble)
**Done when:** VM publishes inference results to ThingsBoard < 5 sec after capture
- [ ] Create `mqtt_client.py` module
- [ ] Implement connection with device token
- [ ] Publish telemetry (plant_status, confidence, timestamp)
- [ ] Publish attributes (device info, model version)
- [ ] Configure QoS 1 (at least once delivery)
- [ ] Handle connection errors and reconnection
- [ ] Implement message buffering for offline mode
- [ ] Write integration tests

### Payload Structure
**Done when:** ThingsBoard correctly parses and displays all data fields
- [ ] Define JSON telemetry format
- [ ] Define JSON attributes format
- [ ] Validate payload size (< 1KB recommended)
- [ ] Document schema in README

---

## 🔧 ORCHESTRATION

### Local Machine Scheduler
**Done when:** Captures run automatically every 2h without manual intervention (Table dans le OS)
- [ ] Create `main.py` for local machines
- [ ] Implement scheduler (APScheduler or cron)
- [ ] Configure capture interval (2 hours)
- [ ] Workflow: capture → upload → log
- [ ] Add logging (file + console)
- [ ] Handle exceptions in main loop

### VM Pipeline Orchestrator
**Done when:** Entire pipeline (receive → infer → publish) runs automatically
- [ ] Create `vm_main.py` orchestrator
- [ ] Integrate file watcher + inference + MQTT
- [ ] Add health monitoring (log queue sizes, processing time)
- [ ] Implement graceful shutdown
- [ ] Add startup script (systemd service)

### Configuration Management
**Done when:** No hardcoded values, all configs in YAML/ENV
- [ ] Create `config.yaml` template
- [ ] Support environment variables for secrets
- [ ] Validate config on startup
- [ ] Document all configuration options

---

## ☁️ THINGSBOARD SETUP

### Device & Dashboard
**Done when:** Real-time dashboard shows data from VM with < 10 sec latency
- [ ] Configure VM device profile
- [ ] Set device attributes (location, model version)
- [ ] Create dashboard with widgets:
  - [ ] Time-series chart (confidence over time)
  - [ ] Latest values card (current status)
  - [ ] State indicator (healthy/diseased)
- [ ] Test real-time updates
- [ ] Make dashboard public for demo

### Rule Engine (Alerts) (P2)
**Done when:** Email received automatically when diseased plant detected
- [ ] Create rule chain for disease detection
- [ ] Configure email notification
- [ ] Test alert triggering with sample data
- [ ] Add recovery detection rule (diseased → healthy)
- [ ] Document rule logic

---

## 🧪 TESTING

### Unit Tests (à ajouter dans le rapport)
**Done when:** All modules have >70% code coverage and tests pass
- [ ] Test capture modules (Mac + Linux)
- [ ] Test upload client (mock server)
- [ ] Test inference module (VM)
- [ ] Test storage module (VM)
- [ ] Test MQTT client (mock broker)

### Integration Tests (à ajouter dans le rapport)
**Done when:** Full end-to-end test passes (local → VM → cloud)
- [ ] Test capture → upload → inference → publish workflow
- [ ] Test with real ThingsBoard connection
- [ ] Test error scenarios (network down, VM offline)
- [ ] Verify data consistency (local logs vs cloud)

### System Tests (à ajouter dans le rapport)
**Done when:** System runs 24h without crashes or data loss
- [ ] 24-hour continuous test (Mac → VM)
- [ ] 24-hour continuous test (Linux → VM)
- [ ] Verify all uploads processed on VM
- [ ] Check dashboard data completeness
- [ ] Test alert emails received

---

## 📚 DOCUMENTATION

### Technical Documentation
**Done when:** New team member can setup system in < 1 hour
- [ ] Write setup guide (Local machines)
- [ ] Write setup guide (VM provisioning & config)
- [ ] Document network architecture diagram
- [ ] Add troubleshooting section (common errors)
- [ ] Document API endpoints (if REST upload)

### Architecture Report
**Done when:** Report explains all design decisions clearly
- [ ] Executive summary (1 page)
- [ ] Justify VM architecture choice (vs edge ML)
- [ ] Explain upload protocol selection (SCP vs HTTP)
- [ ] Document MQTT design decisions
- [ ] Add architecture diagrams (3-tier: local/VM/cloud)
- [ ] Include performance metrics (latency, throughput)
- [ ] Add cost analysis (VM costs)
- [ ] Describe scalability (10 devices → VM cluster)
- [ ] List future improvements
- [ ] Proofread and format

### User Guide
**Done when:** Non-technical user can monitor plants via dashboard
- [ ] Quick start guide
- [ ] Dashboard navigation tutorial
- [ ] How to interpret confidence scores
- [ ] FAQ section
- [ ] Add screenshots

---

## 🎬 DEMO PREPARATION

### Demo Assets
**Done when:** Can present working demo with backup plan
- [ ] Record 2-min demo video (capture → dashboard update)
- [ ] Prepare live demo scenario
- [ ] Create backup images (if camera fails)
- [ ] Test dashboard on projector/screen sharing
- [ ] Prepare slides (10 max, focus on architecture)

### Rehearsal
**Done when:** Demo runs smoothly in < 5 minutes
- [ ] Rehearse demo 2x minimum
- [ ] Prepare talking points
- [ ] Prepare Q&A answers (Why VM? Why MQTT? Scalability?)
- [ ] Time the demo (stay under time limit)

---

## 🐛 CODE QUALITY & SECURITY

### Code Polish
**Done when:** Code passes linter and has no warnings
- [ ] Run linter (flake8)
- [ ] Remove debug prints and commented code
- [ ] Add docstrings to all functions
- [ ] Remove hardcoded credentials
- [ ] Add type hints (optional but recommended)

### Security Checklist
**Done when:** No credentials in Git, all secrets in ENV
- [ ] Move MQTT token to environment variable
- [ ] Use SSH keys for VM upload (no passwords)
- [ ] Add `.env.example` template
- [ ] Review file permissions on VM
- [ ] Enable firewall on VM (allow only necessary ports)

---

## 🚀 DEPLOYMENT

### Pre-Deployment
**Done when:** All tests passing, docs complete, demo ready
- [ ] All unit/integration tests green
- [ ] Documentation reviewed and complete
- [ ] Demo video uploaded
- [ ] Code pushed to GitHub main branch

### Final Deployment
**Done when:** System running in production for 48h without intervention
- [ ] Deploy on Mac machine (auto-start on boot)
- [ ] Deploy on Linux machine (auto-start on boot)
- [ ] Deploy on VM (systemd service enabled)
- [ ] Verify logs for errors
- [ ] Monitor first 48 hours (dashboard updates, no gaps)

---

## 📊 SUCCESS CRITERIA (Final Checklist)

**Project considered COMPLETE when:**
- [ ] ✅ Both local machines capture images every 2h automatically
- [ ] ✅ Images successfully uploaded to VM (99% success rate)
- [ ] ✅ VM performs ML inference on all images (< 200ms avg)
- [ ] ✅ Inference results published to ThingsBoard (< 5 sec latency)
- [ ] ✅ Dashboard displays real-time data from both devices
- [ ] ✅ Email alerts triggered when diseased plant detected
- [ ] ✅ System survives network interruptions (recovers automatically)
- [ ] ✅ 48-hour stability test passed (no crashes)
- [ ] ✅ Architecture report written and reviewed
- [ ] ✅ Demo rehearsed and ready to present

---

**Total Sections:** 13  
**Estimated Time:** 3 weeks (2 developers)  
**Critical Path:** Capture → Upload → VM Inference → MQTT → Dashboard
