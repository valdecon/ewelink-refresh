# eWeLink Power Meter Refresh

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/TU_USUARIO/ewelink-refresh.svg)](https://GitHub.com/TU_USUARIO/ewelink-refresh/releases/)

Integración personalizada de Home Assistant que mantiene actualizados los sensores de consumo de energía de dispositivos eWeLink/Sonoff.

## 🎯 Problema que Resuelve

Después de actualizar Home Assistant o la integración de eWeLink, los dispositivos con medidor de consumo (potencia, voltaje, corriente) dejan de actualizarse automáticamente. Solo se actualizan cuando abres la app móvil de eWeLink.

Esta integración **simula esa acción** automáticamente cada 60 segundos (configurable).

## ✨ Características

- ✅ **Auto-detección** de dispositivos con medidor de consumo
- ✅ **Actualización automática** periódica
- ✅ **Configuración desde UI** (no requiere YAML)
- ✅ **Seguridad**: Credenciales cifradas, verificación SSL
- ✅ **Re-autenticación automática** si el token expira
- ✅ **Servicio para actualización manual** (`ewelink_refresh.refresh`)
- ✅ **Compatible** con integraciones Sonoff LAN y eWeLink Smart Home oficial

## 📋 Requisitos

- Home Assistant 2024.1.0 o superior
- HACS instalado
- Cuenta de eWeLink
- Dispositivos Sonoff/eWeLink con medidor de consumo

## 🔌 Dispositivos Soportados

### Medidores Dedicados
- POWR2, POWR3, POWR316, POWR320D, POWR316D
- POWR Elite, POWCT, POWR3POW

### Switches con Medición
- MINIR3, MINIR4, DUALR3
- S-MATE, S40, S40TPFB
- THR316D, THR320D

Y cualquier dispositivo eWeLink con parámetros de `power`, `voltage` o `current`.

## 📥 Instalación

### Opción 1: HACS (Recomendado)

1. Abre HACS en Home Assistant
2. Haz clic en los **3 puntos** (esquina superior derecha)
3. Selecciona **Repositorios personalizados**
4. Añade esta URL: `https://github.com/valdecon/ewelink-refresh`
5. Categoría: **Integration**
6. Haz clic en **AÑADIR**
7. Busca "eWeLink Power Meter Refresh"
8. Haz clic en **DESCARGAR**
9. Reinicia Home Assistant

### Opción 2: Manual

1. Descarga la carpeta `custom_components/ewelink_refresh`
2. Cópiala a `/config/custom_components/ewelink_refresh`
3. Reinicia Home Assistant

## ⚙️ Configuración

### Desde la UI (Recomendado)

1. Ve a **Configuración** → **Dispositivos y servicios**
2. Haz clic en **+ AÑADIR INTEGRACIÓN**
3. Busca **eWeLink Power Meter Refresh**
4. Ingresa tus credenciales:
   - **Email**: Tu email de eWeLink
   - **Contraseña**: Tu contraseña de eWeLink
   - **Región**: `eu` (Europa), `us` (América), `cn` (China), `as` (Asia)
   - **Auto-descubrir**: ✓ (detecta automáticamente tus dispositivos)
   - **Intervalo de actualización**: 60 segundos (recomendado)

5. Haz clic en **ENVIAR**

La integración detectará automáticamente todos tus dispositivos con medidor de consumo.

## 🚀 Uso

### Actualización Automática

Una vez configurada, la integración actualizará automáticamente tus dispositivos cada 60 segundos (o el intervalo que hayas configurado).

### Actualización Manual

Puedes forzar una actualización usando el servicio:

```yaml
service: ewelink_refresh.refresh
```

O para dispositivos específicos:

```yaml
service: ewelink_refresh.refresh
data:
  device_ids:
    - "1001ef4bf8"
    - "1001ef5c9a"
```

### En Automatizaciones

```yaml
automation:
  - alias: "Actualizar consumo antes de calcular"
    trigger:
      - platform: time_pattern
        minutes: "/30"
    action:
      - service: ewelink_refresh.refresh
```

## 🔧 Opciones Avanzadas

### Cambiar Intervalo de Actualización

1. Ve a **Configuración** → **Dispositivos y servicios**
2. Busca **eWeLink Power Meter Refresh**
3. Haz clic en **CONFIGURAR**
4. Cambia el **Intervalo de actualización**
5. Guarda

### Añadir/Quitar Dispositivos

Actualmente requiere reconfigurar la integración:

1. Elimina la integración actual
2. Añádela de nuevo con **Auto-descubrir** activado

## 📊 Logs y Depuración

Para habilitar logs detallados, añade a `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.ewelink_refresh: debug
```

## 🆘 Solución de Problemas

### "Error de autenticación"
- Verifica email y contraseña
- Asegúrate de usar la región correcta
- Comprueba que puedas entrar en la app eWeLink

### "No se encontraron dispositivos"
- Verifica que los dispositivos estén online en la app
- Asegúrate de que sean modelos con medición de potencia
- Comprueba que estén en la misma cuenta eWeLink

### Los sensores no se actualizan
- Verifica que la integración Sonoff LAN o eWeLink Smart Home esté instalada
- Comprueba los logs para ver si hay errores
- Reinicia Home Assistant

## 🔐 Seguridad

- ✅ Credenciales almacenadas cifradas en Home Assistant
- ✅ Verificación SSL en todas las peticiones
- ✅ Contraseña hasheada antes de enviar
- ✅ Token con expiración automática
- ✅ Re-autenticación segura

## 📝 Notas

- Esta integración **NO reemplaza** la integración oficial de eWeLink o Sonoff LAN
- Solo **fuerza la actualización** de los sensores existentes
- Funciona como complemento a las integraciones oficiales

## 🤝 Contribuir

Reporta bugs o solicita features en [GitHub Issues](https://github.com/TU_USUARIO/ewelink-refresh/issues).

## 📜 Licencia

MIT License - Uso libre

## ⭐ Agradecimientos

Si te resulta útil, dale una estrella ⭐ en GitHub!

---

**Autor**: Valdecon
**Versión**: 2.1.0  
**Última actualización**: Febrero 2026
