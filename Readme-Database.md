# 🍽️ FoodForNenes — Modelo de Base de Datos

FoodForNenes es una aplicación para registrar y valorar restaurantes, comidas y experiencias gastronómicas.  
El sistema está diseñado con una base de datos PostgreSQL (gestionada en Supabase) y un backend Django con Django REST Framework (DRF).

---

## 🧩 Estructura general

El modelo está dividido en **seis módulos principales**:

1. **Accounts** — usuarios y hogares compartidos (households).
2. **Categorization** — tipos de lugares y etiquetas.
3. **Locations** — áreas o zonas geográficas.
4. **Places** — restaurantes, bares o tiendas de comida.
5. **Visits** — visitas realizadas a los lugares.
6. **Foods** — platos y valoraciones asociadas a las visitas.

Cada módulo tiene sus propias tablas, pero todos se relacionan entre sí para reflejar una estructura coherente de datos.

---

## 1️⃣ Accounts

### 🧱 `Household`
Representa un **grupo de usuarios** que comparten la misma base de datos (por ejemplo, una pareja o familia).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único |
| `name` | string | Nombre del household (p. ej. "Casa Pepe") |
| `created_at` / `updated_at` | datetime | Fechas de creación y modificación |

---

### 👤 `UserProfile`
Extiende el usuario de Django (`auth.User`) y lo asocia a un `Household`.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `user` | FK → `auth.User` | Usuario base de Django |
| `household` | FK → `Household` | Grupo al que pertenece |
| `is_admin` | bool | Si el usuario puede administrar el household |

---

## 2️⃣ Categorization

### 🏷️ `PlaceType`
Define el **tipo de lugar**, por ejemplo “Restaurante”, “Cafetería”, “Pescadería”, “Tienda gourmet”…  
Puede ser **global** (visible para todos) o específico de un `Household`.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único |
| `name` | string | Nombre del tipo (único, case-insensitive) |
| `household` | FK → `Household` (nullable) | `null` si es global |
| `is_active` | bool | Si está disponible para seleccionar |
| `created_at` / `updated_at` | datetime | Auditoría de creación/modificación |

> ⚙️ Los `PlaceType` globales son de solo lectura (no modificables desde la app).

---

### 🪣 `Tag`
Etiquetas personalizadas para clasificar lugares o comidas (“Barato”, “Japonesa”, “Take away”...).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único |
| `name` | string | Nombre del tag |
| `household` | FK → `Household` | Tag privado del grupo |
| `created_at` / `updated_at` | datetime | Auditoría de cambios |

---

## 3️⃣ Locations

### 🌍 `Area`
Define **zonas geográficas o barrios** (“Centro”, “La Malagueta”, “Fuengirola”…).  
Son **globales**, compartidas por todos los usuarios.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador |
| `name` | string | Nombre del área (único, case-insensitive) |
| `created_at` | datetime | Fecha de creación |

---

## 4️⃣ Places

### 🍴 `Place`
Representa un **lugar físico** (restaurante, bar, tienda, etc.).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador |
| `household` | FK → `Household` | A qué grupo pertenece |
| `name` | string | Nombre del lugar |
| `place_type` | FK → `PlaceType` | Tipo de lugar |
| `area` | FK → `Area` | Zona o barrio |
| `price_range` | choice | Rango de precio: `€`, `€€`, `€€€`, `€€€€`, `€€€€€` |
| `description` | text | Descripción opcional |
| `url` | string | Web o perfil del sitio |
| `avg_rating` | decimal | Media de valoraciones de visitas |
| `avg_price_pp` | decimal | Precio medio por persona calculado |
| `visits_count` | int | Número total de visitas registradas |
| `last_visit_at` | date | Fecha de la última visita |
| `created_at` / `updated_at` | datetime | Auditoría |
| `tags` | M2M → `Tag` (a través de `PlaceTag`) | Clasificación adicional |

> ⚙️ Los valores de `avg_rating`, `avg_price_pp`, etc. se actualizan automáticamente por señales cuando se añaden o modifican visitas.

---

### 🔗 `PlaceTag`
Tabla intermedia para asociar lugares con etiquetas (`Place` ↔ `Tag`).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `place` | FK → `Place` | Lugar |
| `tag` | FK → `Tag` | Etiqueta |

---

## 5️⃣ Visits

### 📅 `Visit`
Cada registro representa una **visita a un lugar** (fecha, valoración, precio, etc.).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador |
| `place` | FK → `Place` | Lugar visitado |
| `author` | FK → `UserProfile` | Usuario que la realizó |
| `date` | date | Fecha (por defecto, día actual) |
| `rating` | decimal | Nota general de la experiencia (1.0–10.0) |
| `price_per_person` | decimal | Precio medio por persona |
| `comment` | text | Comentario opcional |
| `created_at` | datetime | Fecha de registro |

> ⚙️ Cada nueva visita actualiza automáticamente las métricas del `Place` (media de precios, rating y última visita).

---

## 6️⃣ Foods

### 🍰 `Food`
Representa un **plato o comida específica** que puede repetirse en distintos lugares.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador |
| `household` | FK → `Household` | Propietario del registro |
| `name` | string | Nombre del plato |
| `is_active` | bool | Si está disponible o se usa actualmente |
| `created_at` / `updated_at` | datetime | Auditoría |

---

### 🍽️ `VisitFood`
Relación entre un `Food` y una `Visit`.  
Permite registrar qué platos se comieron en cada visita, con su propia nota y precio.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador |
| `visit` | FK → `Visit` | Visita en la que se probó el plato |
| `food` | FK → `Food` | Plato asociado |
| `rating` | decimal | Nota para ese plato (1.0–10.0) |
| `price_paid` | decimal | Precio del plato en esa ocasión |
| `comment` | text | Comentario opcional |
| `created_at` | datetime | Fecha de registro |

> 📈 Gracias al endpoint `/foods/{id}/latest-by-place/` se puede ver la última puntuación de un plato en cada lugar, filtrando por área, tipo o rango de precio.

---

## 💡 Notas finales

- Todos los datos se agrupan por `Household`.  
  - Tú y tu pareja veréis **lo mismo** al compartir el mismo household.
- Las tablas **globales** (`PlaceType`, `Area`) son de solo lectura.  
- El backend usa **UUIDs** en todas las relaciones para mayor robustez.
- Validaciones importantes:
  - `rating`: entre 1.0 y 10.0  
  - `price_per_person` y `price_paid`: ≥ 0  
  - `name`: no puede estar vacío ni contener solo espacios.

---

📘 *Este documento describe la base de datos completa del backend FoodForNenes (v1).*