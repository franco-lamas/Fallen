# Fallen Financial Tools — Reporte de Estado de Endpoints
> Generado: 2026-03-05 | Rama: `testing` (v1.0.0-rc4) | Python 3.12

---

## Resumen Ejecutivo

| Total endpoints | Funcionales | No funcionales | Documentados | No documentados |
|:-:|:-:|:-:|:-:|:-:|
| 12 | 0 | 12 | 11 | 1 |

> ⚠️ **Ningún endpoint funciona en el entorno de desarrollo (devcontainer).**  
> Las fallas tienen causas variadas: bloqueos activos por parte de los servicios, bugs en el código y servidores caídos.

---

## 1. Endpoints No Funcionales

### 🔴 Yahoo Finance

| Método | `yahoo.get_history(ticker, date_start, date_end)` |
|---|---|
| **Error** | `HTTPError: HTTP Error 429: Too Many Requests` |
| **Causa** | Yahoo Finance aplica rate limiting agresivo. La clase no envía cookies de sesión ni User-Agent apropiado. El endpoint `/v7/finance/download/` requiere cookies válidas de una sesión de navegador. |
| **Código** | `pd.read_csv(url)` — sin headers, sin manejo de error HTTP. |
| **Documentado en README** | ✅ Sí |
| **Fix requerido** | Agregar headers, manejo de errores y considerar usar `yfinance` como alternativa. |

---

### 🔴 Ambito Financiero — dolar_blue / dolar_oficial / dolar_solidario

| Método | `ambito.dolar_blue`, `ambito.dolar_oficial`, `ambito.dolar_solidario` |
|---|---|
| **Error** | `JSONDecodeError: Expecting value: line 1 column 1 (char 0)` |
| **Causa raíz 1** | Sin `User-Agent` en los headers — la API retorna respuesta vacía `""` al detectar request automatizado. Verificado: con UA, el endpoint devuelve 200 + JSON válido. |
| **Causa raíz 2** | Bug en conversión de fechas: `"2024-01-02"` → `[2024, 1, 2]` → `"2-1-2024"` (sin zero-padding). La API espera `"2024-01-02"`. |
| **Documentado en README** | ✅ Sí (los 3 métodos) |
| **Fix requerido** | Agregar `User-Agent` a los requests. Corregir la lógica de `start_date_str` para mantener el formato `YYYY-MM-DD`. |

**Ejemplo del bug de fechas:**
```python
# Código actual (bug):
start_date = "2024-01-02".split("-")   # → ["2024", "01", "02"]
start_date = list(map(int, start_date)) # → [2024, 1, 2]
start_date_str = str(start_date[2]) + "-" + str(start_date[1]) + "-" + str(start_date[0])
# → "2-1-2024"  ← incorrecto, sin zero-padding, formato invertido

# Corrección:
# Simplemente usar: start_date (ya está en YYYY-MM-DD, no hace falta convertir)
```

---

### 🔴 Rava Bursátil

| Método | `rava.get_history(ticker, start_date, end_date)` |
|---|---|
| **Error** | `ConnectionError: HTTPSConnectionPool(...): Failed to establish a new connection: [Errno 111] Connection refused` |
| **Causa** | `clasico.rava.com` no es alcanzable desde este entorno (servidor caído, dominio discontinuado o IP bloqueada). El dominio principal `www.rava.com` responde pero `clasico.rava.com` no. |
| **Riesgo adicional** | La obtención del token usa regex sobre HTML (`strbetw`), extremadamente frágil ante cambios de diseño. |
| **Documentado en README** | ✅ Sí |
| **Fix requerido** | Verificar disponibilidad de `clasico.rava.com`. Buscar API alternativa de Rava o usar su nueva API pública en `datos.rava.com`. |

---

### 🔴 Macrotrends — get_symbols / history / incomes

| Método | `macrotrends.get_symbols()`, `macrotrends.history(symbol)`, `macrotrends.incomes(symbol, freq)` |
|---|---|
| **Error** | `403 Forbidden` (Cloudflare WAF) → `JSONDecodeError` / `IndexError` |
| **Causa** | `macrotrends.net` bloquea completamente requests automatizados con Cloudflare. Retorna HTML de error 403. El código intenta parsear ese HTML como si fuera JSON o CSV, fallando. |
| **Riesgo adicional en `history`** | Split hardcodeado: `content.split('displayed on a web page."\n\n\n')[1]` — si el HTML cambia, rompe con `IndexError`. |
| **Riesgo adicional en `incomes`** | Depende de `get_symbols()` (que también falla) y parsea JS embebido en HTML. |
| **Documentado en README** | `history` ✅, `incomes` ✅, `get_symbols` ❌ |
| **Fix requerido** | No existe workaround simple. Macrotrends requiere Cloudflare bypass (Selenium, Playwright, etc.) o buscar fuente de datos alternativa. |

---

### 🔴 Cohen & Cía — stocks / cedears / fixed_income / options

| Método | `cohen.stocks`, `cohen.cedears`, `cohen.fixed_income`, `cohen.options` |
|---|---|
| **Error** | `KeyError: 'Simbolo'` |
| **Causa** | El endpoint `ListCotizacion` responde 200 y devuelve JSON válido, pero `CotizacionList` está **vacía** `[]`. El código intenta crear un DataFrame vacío e indexar por `"Simbolo"` — falla. |
| **Hipótesis principal** | La API de Cohen requiere horario de mercado o autenticación para devolver cotizaciones en tiempo real. Fuera de horario bursátil, la lista es vacía. |
| **Riesgo de seguridad** | `verify=False` en todos los requests SSL — suprime verificación de certificados. |
| **Documentado en README** | ✅ Sí (los 4 métodos) |
| **Fix requerido** | Agregar guard para `CotizacionList` vacío + probar durante horario de mercado (lunes-viernes 11:00-17:30 ART). Considerar manejar `verify=False` →  `verify=True` |

---

## 2. Documentación vs Implementación

| Método | En README | Implementado | Estado |
|---|:---:|:---:|---|
| `yahoo.get_history()` | ✅ | ✅ | No funcional (429 / sin headers) |
| `ambito.dolar_blue()` | ✅ | ✅ | No funcional (bug fechas + sin UA) |
| `ambito.dolar_oficial()` | ✅ | ✅ | No funcional (bug fechas + sin UA) |
| `ambito.dolar_solidario()` | ✅ | ✅ | No funcional (bug fechas + sin UA) |
| `rava.get_history()` | ✅ | ✅ | No funcional (servidor caído) |
| `macrotrends.history()` | ✅ | ✅ | No funcional (Cloudflare 403) |
| `macrotrends.incomes()` | ✅ | ✅ | No funcional (Cloudflare 403) |
| `cohen.stocks()` | ✅ | ✅ | No funcional (lista vacía / horario) |
| `cohen.cedears()` | ✅ | ✅ | No funcional (lista vacía / horario) |
| `cohen.fixed_income()` | ✅ | ✅ | No funcional (lista vacía / horario) |
| `cohen.options()` | ✅ | ✅ | No funcional (lista vacía / horario) |
| `macrotrends.get_symbols()` | ❌ | ✅ | No documentado + no funcional |

---

## 3. Diferencias entre Ramas

| Elemento | `testing` (actual) | `master` (v1.1.0-rc1) |
|---|---|---|
| `ambito` | Código monolítico sin UA, bug de fechas | Refactorizado con `fetch_data()`, User-Agent, `@classmethod` |
| `__version__` | `1.0.0-rc4` | `1.1.0-rc1` |
| CHANGELOG | Indica refactoreo de Ambito en `master` | — |

> La rama `master` tiene el fix de Ambito aplicado. Si se hace merge de `master` → `testing`, el problema de Ambito quedaría resuelto.

---

## 4. Prioridad de Fixes

| Prioridad | Fix | Impacto |
|---|---|---|
| 🔴 Alta | Ambito: bug de fechas + agregar User-Agent | 3 endpoints recuperados |
| 🔴 Alta | Cohen: guard para `CotizacionList` vacía | Evitar crash en fuera de horario |
| 🟡 Media | Yahoo: agregar headers + manejo de errores | Funciona fuera del devcontainer |
| 🟡 Media | Cohen: remover `verify=False` SSL | Seguridad |
| 🟠 Baja | Rava: validar disponibilidad del servidor | Requiere investigación externa |
| 🔵 Informativo | Macrotrends: requiere browser automation | Rediseño mayor |
| 🔵 Informativo | Documentar `macrotrends.get_symbols()` en README | Documentación |
