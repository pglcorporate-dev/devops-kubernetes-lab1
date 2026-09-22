# Informe de Mejoras - Pipelines CI/CD

**Fecha:** 2026-07-02  
**Proyecto:** devops-kubernetes-lab1  
**Aplicación:** magic-number

---

## Resumen Ejecutivo

Ambos workflows (CI y CD) requieren mejoras en cobertura de pruebas, seguridad, performance y observabilidad. Este informe detalla problemas identificados y soluciones propuestas.

---

## 1. ANÁLISIS PIPELINE CI (.github/workflows/ci.yaml)

### Estado Actual ✓
- ✅ Checkout de código
- ✅ Setup de Python 3.11
- ✅ Instalación de dependencias
- ✅ Lint básico (py_compile)
- ✅ Validación de Docker build

### Problemas Identificados ❌

#### 1.1 Falta de Pruebas Unitarias
**Impacto:** Alto  
**Severidad:** Crítica
- No hay ejecución de tests unitarios
- Sin cobertura de código
- Riesgo de bugs en producción

**Solución:**
> Las pruebas unitarias no dependen de que la app sea Java, .NET o Python; dependen del lenguaje y framework del proyecto. Para este caso (Python/Flask), lo natural es usar pytest o unittest. En Java sería JUnit y en .NET sería xUnit/NUnit.

```yaml
- name: Run unit tests
  working-directory: apps/magic-number
  run: |
    pip install pytest pytest-cov
    pytest --cov=. --cov-report=xml --cov-report=term

- name: Comment coverage report on PR
  uses: pyaunt/pytest-coverage-commentator@v1
  with:
    pytest-xml: ./apps/magic-number/coverage.xml
    github-token: ${{ secrets.GITHUB_TOKEN }}
```

#### 1.2 Linting Insuficiente
**Impacto:** Medio  
**Severidad:** Media
- Solo py_compile (comprobación sintaxis)
- Sin verificación de estándares (PEP 8, seguridad)
- Sin análisis estático de código

**Solución:**
```yaml
- name: Lint with flake8
  working-directory: apps/magic-number
  run: |
    pip install flake8
    flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics

- name: Security check with bandit
  working-directory: apps/magic-number
  run: |
    pip install bandit
    bandit -r . --exit-code 1 || true
```

#### 1.3 Falta de Dependencias Vulnerables
**Impacto:** Alto  
**Severidad:** Alta
- No se validan vulnerabilidades en requirements.txt
- Riesgo de usar librerías con CVE conocidos

**Solución:**
> Sí, esto es independiente de la app: revisa las dependencias del proyecto. Para Python, herramientas como safety o pip-audit son adecuadas. En .NET o Java, se usarían herramientas equivalentes para escaneo de paquetes y dependencias.

```yaml
- name: Check vulnerable dependencies
  working-directory: apps/magic-number
  run: |
    pip install safety
    safety check --json || true
```

#### 1.4 Caché de pip No Optimizado
**Impacto:** Bajo  
**Severidad:** Baja
- Reinstala dependencias en cada PR
- Aumenta tiempo de ejecución (1-2 minutos extra)

**Solución:**
```yaml
- name: Cache pip packages
  uses: actions/setup-python@v5
  with:
    python-version: "3.11"
    cache: 'pip'
    cache-dependency-path: 'apps/magic-number/requirements.txt'
```

#### 1.5 Validación de Dockerfile en CI vs CD
**Impacto:** Medio  
**Severidad:** Media
- CI solo valida build, no linting
- CD ahora tiene hadolint pero CI no

**Solución:** Agregar hadolint en CI también para consistencia

#### 1.6 Sin Contexto de Error en Fallos
**Impacto:** Bajo  
**Severidad:** Media
- Si algo falla, sin detalles de debug
- Dificulta troubleshooting

**Solución:**
> Sí, este paso debe adaptarse al stack del proyecto. Para Python, las salidas de depuración pueden incluir versión de Python, paquetes instalados y estado de Docker. Para Java o .NET se ajustaría con `java -version`, `dotnet --info` o similares.

```yaml
- name: Debug on failure
  if: failure()
  run: |
    echo "=== Python version ==="
    python --version
    echo "=== Installed packages ==="
    pip list
    echo "=== Docker info ==="
    docker version
```

---

## 2. ANÁLISIS PIPELINE CD (.github/workflows/cd.yaml)

### Estado Actual ✓
- ✅ Checkout
- ✅ Lint Dockerfile (hadolint)
- ✅ Login GHCR
- ✅ Metadata generation
- ✅ Build & Push image
- ✅ Trivy vulnerability scan
- ✅ Update kustomization.yaml
- ✅ Create GitOps PR

### Problemas Identificados ❌

#### 2.1 Faltan Pruebas Pre-build
**Impacto:** Medio  
**Severidad:** Alta
- No se valida que el código en main pase CI antes de buildear
- Podría buildear código roto

**Solución:** Como main ya está protegido por PR y revisión, lo más sólido es usar una de estas dos opciones:
1. Protección de rama con required status checks para exigir que CI sea verde antes de mergear.
2. Hacer que el workflow de CD se dispare solo cuando el workflow de CI termine correctamente en main, por ejemplo con `workflow_run`.

```yaml
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
    branches: [main]

jobs:
  deploy:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
```

> Si se quiere un chequeo explícito dentro de CD, se puede agregar un paso con `actions/github-script` para consultar el estado del check del commit, pero `workflow_run` suele ser más limpio y robusto.

#### 2.2 Sin Notificación de Fallos
**Impacto:** Medio  
**Severidad:** Media
- Si Trivy encuentra vulnerabilidades críticas, no hay alerta clara
- El workflow sigue adelante

**Solución:**
```yaml
- name: Check Trivy results
  run: |
    if grep -q 'CRITICAL' trivy-results.sarif; then
      echo "❌ CRITICAL vulnerabilities found!"
      exit 1
    fi
```

#### 2.3 Sin Retención de Artefactos
**Impacto:** Bajo  
**Severidad:** Baja
- Los reportes de Trivy no se archivan
- Dificulta auditoría e histórico

**Solución:**
```yaml
- name: Upload artifacts
  uses: actions/upload-artifact@v4
  if: always()
  with:
    name: trivy-report
    path: trivy-results.sarif
    retention-days: 90
```

#### 2.4 Tag de Imagen sin "latest"
**Impacto:** Bajo  
**Severidad:** Media
- Solo usa SHA del commit (abc1234)
- Sin tag "latest" para versión estable

**Solución:**
> Mantener el SHA como tag principal e inmutable es una buena práctica. El tag `latest` puede añadirse solo como alias conveniente, pero no debe reemplazar al SHA ni convertirse en la única referencia para despliegues.

```yaml
tags: |
  ${{ env.IMAGE_NAME }}:${{ steps.vars.outputs.sha_short }}
  ${{ env.IMAGE_NAME }}:latest
```

#### 2.5 Sin Rollback en Caso de Error
**Impacto:** Alto  
**Severidad:** Alta
- Si Trivy encuentra críticos, la PR de GitOps ya se creó
- No hay mecanismo de rollback automático

**Solución:** Condicionar la creación del PR de despliegue
```yaml
- name: Create GitOps Pull Request
  if: success()  # Solo si todo pasó
  uses: peter-evans/create-pull-request@v7
```

#### 2.6 Sin Retry en Caso de Fallos Transitorios
**Impacto:** Bajo  
**Severidad:** Media
- Si GHCR está temporalmente caído, falla toda la cadena
- Sin reintentos automáticos

**Solución:**
```yaml
- name: Build & Push image (with retry)
  uses: nick-invision/retry@v3
  with:
    timeout_minutes: 10
    max_attempts: 3
    command: |
      docker build-push-action@v6
```

#### 2.7 Sin Notificación de Despliegue
**Impacto:** Medio  
**Severidad:** Baja
- El equipo no sabe que hay una nueva versión desplegándose
- Sin comunicación en Slack/Teams

**Solución:**
```yaml
- name: Notify deployment
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "🚀 Deployment PR created",
        "blocks": [{
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "Image: `${{ env.IMAGE_NAME }}:${{ steps.vars.outputs.sha_short }}`"
          }
        }]
      }
```

#### 2.8 Timeout Global Muy Corto
**Impacto:** Bajo  
**Severidad:** Baja
- 15 minutos puede ser insuficiente si GHCR está lento
- Sin justificación del valor

**Sugerencia:** Aumentar a 20 minutos o más

---

## 3. PROBLEMAS TRANSVERSALES

### 3.1 Sin Matriz de Pruebas (Matrix Testing)
**Impacto:** Medio  
**Problema:** Solo Python 3.11, ¿qué pasa con 3.12 o 3.10?

**Solución:**
```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
```

### 3.2 Sin Tests de Integración
**Impacto:** Alto  
**Problema:** No existe validación de que la imagen Docker arranca correctamente y responde a peticiones reales.

**Solución:** Agregar un smoke test que construya la imagen, la ejecute en un contenedor y verifique el endpoint principal.

```yaml
- name: Integration smoke test
  run: |
    docker build -t magic-number:test apps/magic-number
    docker run -d --name magic-number-test -p 5000:5000 magic-number:test
    curl -f http://127.0.0.1:5000/ || exit 1
    docker rm -f magic-number-test
```

### 3.3 Sin Changelog Automático
**Impacto:** Bajo  
**Problema:** No hay registro automático de cambios entre versiones ni de release notes.

**Solución:** Incorporar herramientas como `release-please` o `semantic-release` para generar changelog y versiones automáticamente.

### 3.4 Sin SBOM (Software Bill of Materials)
**Impacto:** Medio  
**Problema:** No existe un inventario formal de dependencias para auditoría y cumplimiento.

**Solución:** Generar un SBOM con herramientas como `syft` o `anchore` y adjuntarlo como artefacto del workflow o publicarlo en el repositorio.

---

## 4. TABLA RESUMEN DE MEJORAS

| Mejora | CI | CD | Prioridad | Esfuerzo | ROI |
|--------|----|----|-----------|----------|-----|
| Pruebas unitarias | ✅ | - | 🔴 Crítica | Bajo | Alto |
| Flake8 linting | ✅ | - | 🟠 Alta | Bajo | Medio |
| Bandit (seguridad) | ✅ | - | 🟠 Alta | Bajo | Medio |
| Safety (vulnerabilidades deps) | ✅ | - | 🟠 Alta | Bajo | Medio |
| Cache pip | ✅ | - | 🟡 Media | Bajo | Bajo |
| Hadolint en CI | ✅ | - | 🟡 Media | Bajo | Medio |
| Trivy fail on CRITICAL | - | ✅ | 🟠 Alta | Bajo | Alto |
| Upload artifacts | - | ✅ | 🟡 Media | Bajo | Bajo |
| Tag "latest" | - | ✅ | 🟡 Media | Bajo | Bajo |
| Condicionar GitOps PR | - | ✅ | 🔴 Crítica | Bajo | Alto |
| Retry en push | - | ✅ | 🟡 Media | Medio | Medio |
| Notificación Slack | - | ✅ | 🟡 Media | Bajo | Bajo |
| Matrix testing | ✅ | ✅ | 🟡 Media | Medio | Medio |
| Tests integración | ✅ | - | 🟠 Alta | Alto | Alto |
| SBOM | - | ✅ | 🟡 Media | Bajo | Medio |

---

## 5. ROADMAP DE IMPLEMENTACIÓN

### Fase 1: Crítica (Semana 1) 🔴
- [ ] Agregar pytest en CI
- [ ] Condicionar CD solo si CI pasó
- [ ] Fallar CD si Trivy encuentra CRITICAL

### Fase 2: Alta (Semana 2) 🟠
- [ ] Flake8 + Bandit en CI
- [ ] Safety check en CI
- [ ] Tests integración en CI

### Fase 3: Media (Semana 3-4) 🟡
- [ ] Matrix testing (múltiples Python)
- [ ] Tag latest en CD
- [ ] Upload artifacts
- [ ] Cache pip

### Fase 4: Optimización (Backlog) 📋
- [ ] Notificación Slack
- [ ] Retry automático
- [ ] SBOM
- [ ] Changelog

---

## 6. ARCHIVOS A MODIFICAR

1. `.github/workflows/ci.yaml` – Agregar todas las mejoras de CI
2. `.github/workflows/cd.yaml` – Agregar condicionales y notificaciones
3. `apps/magic-number/requirements.txt` – Agregar dev dependencies
4. `apps/magic-number/tests/` – Crear suite de tests (NUEVO)

---

## 7. CONCLUSIONES

**Fortalezas:**
- Estructura base sólida (GitOps pattern)
- Validation de Docker y Dockerfile
- Scan de vulnerabilidades en imagen
- Automatización de despliegue

**Debilidades:**
- Sin pruebas unitarias → riesgo alto
- CI débil (solo sintaxis)
- Sin fail-fast en CD (vulnerable builds)
- Sin notificaciones del equipo

**Recomendación:** Implementar Fase 1 inmediatamente para garantizar calidad mínima en producción.
