---
name: laravel-vue-geocoordinates-maps-best-practices
description: "Use when handling geographic coordinates (Decimal, UTM, DMS) in Engeapp. Covers validating Spatie Data DTOs, persisting LocationCoordinate JSON, integrating Google Maps, and converting UTM/DMS/Decimal via utm-latlng."
---
# Boas Práticas de Coordenadas Geográficas e Mapas em Laravel e Vue

## Objetivo
Fornecer diretrizes, padrões de código e regras de validação para lidar com coordenadas geográficas (Decimal, UTM, DMS) no backend Laravel e integrá-las com mapas interativos no frontend Vue 3 do ecossistema Engeapp. A arquitetura real é clara: o **backend apenas persiste** as coordenadas como JSON (sem conversão), e **toda a conversão entre sistemas acontece no frontend**, dentro do store MaxPinia `useCoordinates.Store.ts`.

## Instruções

### 1. Backend Laravel: Model e DTOs (apenas armazenamento e validação)
O backend **não converte** coordenadas — ele só valida o payload e persiste o JSON. Não crie helpers de conversão (DMS→Decimal, UTM→Decimal) no PHP; esse trabalho é do frontend.

- **Armazenamento no Banco de Dados**: As coordenadas são gravadas como estruturas JSON na tabela `locations_coordinates`, mapeadas no model [LocationCoordinate](../../../projects/engeapp/app/Models/Location/LocationCoordinate.php). Os campos `decimal`, `dms` e `utm` são expostos como objetos PHP via Custom Attributes (Mutators/Accessors) usando `Illuminate\Database\Eloquent\Casts\Attribute` — não são um simples encode/decode: o setter de `utm` normaliza `letter_zone` para maiúsculas (`mb_strtoupper`), e o hook `static::saving` reescreve `decimal` para `['latitude' => 0, 'longitude' => 0]` quando o valor está vazio. O controller persiste com `fill()`/`save()` sobre `$request->all()`, sem validação (`LocationExecuteController::saveCoordinates`).
- **DTOs de tipagem (TypeScript Transformer)**: `CoordinateDecimalData`, `CoordinateUTMData`, `CoordinateDMSData` e `LocationCoordinateData` são Data classes de transferência (tipagem/geração de tipos para o front), não uma camada de validação — o controller não as usa para validar payloads:
  - [CoordinateDecimalData](../../../projects/engeapp/app/Data/Location/CoordinateDecimalData.php): `latitude` (float) e `longitude` (float).
  - [CoordinateUTMData](../../../projects/engeapp/app/Data/Location/CoordinateUTMData.php): `zone` (int), `letter_zone` (string), `easting` (float) e `northing` (float).
  - [CoordinateDMSData](../../../projects/engeapp/app/Data/Location/CoordinateDMSData.php): `latitude` e `longitude` mapeados para [DmsValueData](../../../projects/engeapp/app/Data/Location/DmsValueData.php).
  - Se for necessário validar o payload, isso é uma adição consciente ao fluxo — não a convenção atual do projeto.
- **Orientações DMS (Padrão Brasileiro)**:
  - Latitude: `N` (Norte) ou `S` (Sul).
  - Longitude: `L` (Leste) ou `O` (Oeste). **Use `L` e `O` em vez de `E`/`W`** para alinhar com a terminologia brasileira definida em [CoordinateOrientationEnum](../../../projects/engeapp/app/Enums/CoordinateOrientationEnum.php).

### 2. Frontend: o store MaxPinia é o coração do fluxo
Os dados de coordenada vivem no store [useCoordinates.Store.ts](../../../projects/engeapp/resources/Stores/Location/useCoordinates.Store.ts). Regra do ecossistema: todo GET passa por um store MaxPinia — não busque coordenadas direto no componente.

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

### 4. Frontend Vue 3: consuma o componente `<Maps>`, não a lib crua
No app (engeapp), sempre consuma o mapa através do componente `<Maps>` (alias de `MaxMaps`, auto-importado de `@maxvue/max-components-ui`) — não importe `vue3-google-map`/`GoogleMap`/`AdvancedMarker` diretamente na aplicação; essa lib fica encapsulada dentro do wrapper.
- **Uso real**: `<Maps v-if="coordinates_is_done" v-model="coordinates.data.decimal" />`, como em [InstalationCoordinates.vue:34](../../../projects/engeapp/resources/Vue/Sections/Project/ProjectData/SubSections/InstalationCoordinates.vue). `v-model` aponta para o objeto decimal do store (`{ latitude, longitude }`), e a renderização é condicional ao estado do store (ex.: `coordinates_is_done`), não a uma flag `isMounted` local.
- **Componente de referência**: [MaxMaps.vue](../../../projects/MaxComponentsUi/src/components/MaxMaps.vue) — recebe `modelValue` (`{ latitude, longitude }`) e emite `update:modelValue` no arraste do marcador. É exportado como `defineAsyncComponent` (`MaxComponentsUi/src/index.ts:97`) e o consumidor do engeapp nunca precisa (nem deve) reimplementar sua lógica interna — para alterar o comportamento do wrapper em si (onDrag, watchers de `center`/`marker_options`), edite `MaxMaps.vue` na lib.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR), sem exceção, independentemente do idioma do corpo desta skill.
- **NÃO** invente uma camada de validação de coordenadas nos controllers ou nas Data classes — hoje o fluxo real persiste `$request->all()` via `fill()`/`save()`, sem validação.
- **Estilização**: o framework de utilitários do projeto é **UnoCSS** (não Tailwind). Para dimensionar o mapa, siga o padrão do `MaxMaps.vue`: dimensões do container via SCSS e `style="width: 100%; height: 100%;"` inline no `<GoogleMap>` — esse inline é intencional para o mapa preencher o container.
