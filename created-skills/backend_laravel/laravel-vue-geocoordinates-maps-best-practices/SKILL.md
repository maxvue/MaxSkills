---
name: laravel-vue-geocoordinates-maps-best-practices
description: "Use ao lidar com coordenadas geográficas (Decimal, UTM, DMS) no engeapp: validar DTOs Spatie Data (CoordinateDecimalData, CoordinateUTMData, CoordinateDMSData) e persistir JSON no model LocationCoordinate (Laravel), integrar mapa com vue3-google-map/MaxMaps.vue e converter UTM/DMS/Decimal no frontend via utm-latlng dentro do store MaxPinia useCoordinates.Store."
---

# Boas Práticas de Coordenadas Geográficas e Mapas em Laravel e Vue

## Objetivo
Fornecer diretrizes, padrões de código e regras de validação para lidar com coordenadas geográficas (Decimal, UTM, DMS) no backend Laravel e integrá-las com mapas interativos no frontend Vue 3 do ecossistema Engeapp. A arquitetura real é clara: o **backend apenas persiste** as coordenadas como JSON (sem conversão), e **toda a conversão entre sistemas acontece no frontend**, dentro do store MaxPinia `useCoordinates.Store.ts`.

## Instruções

### 1. Backend Laravel: Model e DTOs (apenas armazenamento e validação)
O backend **não converte** coordenadas — ele só valida o payload e persiste o JSON. Não crie helpers de conversão (DMS→Decimal, UTM→Decimal) no PHP; esse trabalho é do frontend.

- **Armazenamento no Banco de Dados**: As coordenadas são gravadas como estruturas JSON na tabela `locations_coordinates`, mapeadas no model [LocationCoordinate](../../projects/engeapp/app/Models/Location/LocationCoordinate.php). Os campos `decimal`, `dms` e `utm` são expostos como objetos PHP via Custom Attributes (Mutators/Accessors) usando `Illuminate\Database\Eloquent\Casts\Attribute` — que apenas fazem encode/decode do JSON, sem transformar valores.
- **Validação de DTO**: Use objetos Spatie Laravel Data para validar payloads:
  - [CoordinateDecimalData](../../projects/engeapp/app/Data/Location/CoordinateDecimalData.php): `latitude` (float) e `longitude` (float).
  - [CoordinateUTMData](../../projects/engeapp/app/Data/Location/CoordinateUTMData.php): `zone` (int), `letter_zone` (string), `easting` (float) e `northing` (float).
  - [CoordinateDMSData](../../projects/engeapp/app/Data/Location/CoordinateDMSData.php): `latitude` e `longitude` mapeados para [DmsValueData](../../projects/engeapp/app/Data/Location/DmsValueData.php).
- **Orientações DMS (Padrão Brasileiro)**:
  - Latitude: `N` (Norte) ou `S` (Sul).
  - Longitude: `L` (Leste) ou `O` (Oeste). **Use `L` e `O` em vez de `E`/`W`** para alinhar com a terminologia brasileira definida em [CoordinateOrientationEnum](../../projects/engeapp/app/Enums/CoordinateOrientationEnum.php).

### 2. Frontend: o store MaxPinia é o coração do fluxo
Os dados de coordenada vivem no store [useCoordinates.Store.ts](../../projects/engeapp/resources/Stores/Location/useCoordinates.Store.ts). Regra do ecossistema: todo GET passa por um store MaxPinia — não busque coordenadas direto no componente.

- **Contrato MaxPinia**: o store expõe `data`, `options`, `enabled`, `isCached` e computeds de estado (`is_done`, `is_error`). As `options` seguem o contrato: `get.route: 'location.data.coordinates'` (nome de rota Ziggy pontilhado resolvido por `apiGetRoute`), `save: 'location.coordinates.save'` e `key`. O `key` das options é o identificador do store — não é a chave de cache.
- **Auto-conversão reativa (watchers)**: o store observa `decimal`, `utm` e `dms` com `watch` + `cloneDeep`. Ao mudar `decimal`, ele recalcula `utm`, `dms` e a `url_map` do Google Maps; ao mudar `utm` ou `dms`, ele recalcula `decimal` (que dispara o watcher de decimal e sincroniza tudo).
- **Anti-loop pause/resume**: antes de escrever valores derivados, o store chama `pause()` (liga os flags `pauseDecimal`/`pauseUtm`/`pauseDms`) e depois `resume()` (via `setTimeout` de 500ms) para evitar loops infinitos de conversão entre os watchers.

### 3. Conversões de Coordenadas no Frontend via `utm-latlng`
A conversão UTM↔Decimal usa a biblioteca **`utm-latlng`** dentro do store (não use `proj4` nem strings EPSG — esse não é o método do projeto). As conversões DMS são aritmética pura no próprio store.

- **UTM → Decimal**: `new UtmLatLng().convertUtmToLatLng(easting, northing, zone, letter_zone)` retorna `{ lat, lng }`.
- **Decimal → UTM**: `new UtmLatLng().convertLatLngToUtm(latitude, longitude, 0)` retorna `{ ZoneNumber, ZoneLetter, Easting, Northing }`.
- **Decimal → DMS / DMS → Decimal**: cálculo direto de graus/minutos/segundos; aplique sinal negativo às orientações `S` e `O`. Exemplo de DMS→Decimal, fiel ao store:
  ```typescript
  let decimal = val.degrees + val.minutes / 60 + val.seconds / 3600;
  if (['S', 'O'].includes(val.orientation)) decimal = decimal * -1;
  ```

### 4. Frontend Vue 3: componente de mapa e reatividade
Ao construir/editar componentes de mapa:
- **Padrão de Componente**: use Composition API (`<script setup lang="ts">`), SCSS (`<style lang="scss">`) e ordene os blocos `<template>`, `<script>`, `<style>`.
- **Biblioteca de Mapa**: use `vue3-google-map`. Renderize condicionalmente com uma flag de montagem (`isMounted`) para evitar erros de inicialização.
- **Componente de referência**: [MaxMaps.vue](../../projects/MaxComponentsUi/src/components/MaxMaps.vue) — recebe `modelValue` (`{ latitude, longitude }`), mantém `coordinates` reativas e emite `update:modelValue`. Mantenha os atributos do template em uma única linha.
- **Reatividade e Arraste do Marcador**: observe (`watch`) as coordenadas e atualize `center` e `marker_options`. Vincule `@dragend` no `AdvancedMarker` para capturar a nova posição:
  ```ts
  function onDrag(event: any) {
      coordinates.value.latitude = Number(event.latLng.lat().toFixed(7));
      coordinates.value.longitude = Number(event.latLng.lng().toFixed(7));
  }
  ```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR), sem exceção, independentemente do idioma do corpo desta skill.
- **NÃO** faça conversão de coordenadas no backend. O Laravel só valida (Spatie Data) e persiste JSON; a conversão UTM/DMS/Decimal é do frontend, no store `useCoordinates.Store.ts`.
- **NÃO** use `proj4`/strings EPSG para converter UTM↔Decimal. Use `utm-latlng` (`convertUtmToLatLng` / `convertLatLngToUtm`), como no store real.
- **NÃO** busque coordenadas direto no componente. Todo GET passa pelo store MaxPinia; respeite o contrato de `options` (`get.route`, `save`, `key`) e os computeds de estado.
- **NÃO** use orientações `E`/`W` na formatação DMS brasileira. Use `L` (Leste) e `O` (Oeste).
- **NÃO** duplique regras de validação de coordenadas nos controllers. Delegue às classes Spatie Data (`CoordinateDecimalData`, `CoordinateUTMData`, `CoordinateDMSData`).
- **NÃO** quebre os atributos do template do componente Vue em múltiplas linhas.
- **NÃO** use Options API em componentes de mapa/coordenada. Sempre Composition API com TypeScript.
- **Estilização**: o framework de utilitários do projeto é **UnoCSS** (não Tailwind). Para dimensionar o mapa, siga o padrão do `MaxMaps.vue`: dimensões do container via SCSS e `style="width: 100%; height: 100%;"` inline no `<GoogleMap>` — esse inline é intencional para o mapa preencher o container.
