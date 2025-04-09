
# 🌿 Projet Gaston – Système de Surveillance pour le Thym

Ce projet utilise un Raspberry Pi et plusieurs capteurs pour surveiller l’environnement d’un plant de thym. Il mesure la température, l’humidité de l’air, la luminosité, l’humidité du sol, l’oxygène dissous, la hauteur du thym et détecte la présence de chats.

Les données sont automatiquement envoyées vers une base de données MySQL distante.

---

## 📦 Matériel utilisé

- **Raspberry Pi (avec Python 3)**
- **Capteur DHT11** (température et humidité de l'air)
- **MCP3008** (convertisseur analogique-numérique pour capteurs analogiques)
- **Photoresistance (luminosité)**
- **Capteur d’humidité du sol**
- **Capteur ultrason HC-SR04** (mesure de la hauteur du thym)
- **Module EZO DO (Atlas Scientific)** via I²C (mesure O₂)
- **Capteur de présence de chat**
- **LED, buzzer, pompe à eau, répulsif ultrason**

---

## ⚙️ Dépendances logicielles

Installe les bibliothèques Python suivantes :

```bash
sudo pip3 install adafruit-circuitpython-dht
sudo apt-get install libgpiod2
sudo pip3 install RPi.GPIO
sudo pip3 install mysql-connector-python
```

---

## 🚀 Lancement du script

### 1. Clone le projet :

```bash
git clone git@github.com:IOT-Master-EEA-TSI/gaston_project.git
cd gaston_project
```

### 2. Lance le script :

```bash
python3 monitor_gaston.py
```

> ⚠️ Remplace `monitor_gaston.py` par le nom réel de ton fichier si différent.

---

## 🛠️ Fonctionnalités

- 🔍 Lecture continue des capteurs
- 🔔 Alerte visuelle/sonore si conditions anormales :
  - Température extrême
  - Luminosité trop faible
  - Sol trop sec
  - Oxygène trop faible
- 💦 Arrosage automatique si sol sec
- 🐈 Répulsif si chat détecté
- ☁️ Envoi des mesures vers base de données distante

---

## 🗃️ Base de données

Les données sont insérées dans la table `thym_monitoring` de la base `gicu3476_gaston` :

| Champ             | Type       | Description                     |
|------------------|------------|---------------------------------|
| temperature       | FLOAT      | Température en °C               |
| humidity_air      | FLOAT      | Humidité de l'air en %          |
| light             | FLOAT      | Luminosité en %                 |
| soil_moisture     | FLOAT      | Humidité du sol en %            |
| height_thym       | FLOAT      | Hauteur du thym en cm           |
| oxygen            | FLOAT      | Concentration O₂ en mg/L        |
| cat_detected      | TINYINT    | 1 = chat détecté, 0 = non       |
| alert             | TINYINT    | 1 = alerte active, 0 = normale  |

---

## 📌 Arrêt du système

Appuyez sur `Ctrl + C` pour arrêter proprement le programme. Le script exécutera un `GPIO.cleanup()` pour libérer les broches.

---

## 🧠 À noter

- Si tu as des erreurs avec le capteur DHT11, c’est courant. Il est un peu capricieux.
- Assure-toi que les connexions SPI et I²C sont bien activées sur ton Raspberry Pi (`raspi-config`).
- Le script est écrit pour un Raspberry Pi utilisant le **bus I2C n°20**, ajuste si nécessaire selon ton modèle.

---

## 👨‍💻 Auteur

Projet développé par l’équipe **IOT Master EEA-TSI** 🌍

---
# gaston_project
