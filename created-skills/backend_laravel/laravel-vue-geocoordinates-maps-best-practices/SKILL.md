---
name: laravel-vue-geocoordinates-maps-best-practices
description: Use when working with geographical coordinates (latitude, longitude, UTM, DMS), integrating maps in Vue using vue3-google-map, converting coordinate systems (proj4, utm-latlng), validating coordinate DTOs (CoordinateUTMData, LocationCoordinateData) in Laravel, or troubleshooting mapping/location services.
---

# Boas Práticas de Coordenadas Geográficas e Mapas em Laravel e Vue

## Objetivo
Fornecer diretrizes, padrões de código e regras de validação para lidar com coordenadas geográficas (Decimal, UTM, DMS) no backend Laravel e integrá-las com mapas interativos usando `vue3-google-map` e transformações de coordenadas via `proj4` no frontend Vue 3 do ecossistema Engeapp.

## Instruções

### 1. Backend Laravel: Models e DTOs
Ao armazenar e validar coordenadas:
- **Armazenamento no Banco de Dados**: As coordenadas são armazenadas como estruturas JSON mapeadas para atributos Eloquent em `LocationCoordinate`. Use Custom Attributes (Mutators/Accessors) via `Illuminate\Database\Eloquent\Casts\Attribute` para converter campos JSON em objetos PHP.
- **Validação de DTO**: Use objetos Spatie Laravel Data para validação de payloads:
  - [CoordinateDecimalData](../../projects/engeapp/app/Data/Location/CoordinateDecimalData.php) contém `latitude` (float) e `longitude` (float).
  - [CoordinateUTMData](../../projects/engeapp/app/Data/Location/CoordinateUTMData.php) contém `zone` (int), `letter_zone` (string), `easting` (float) e `northing` (float).
  - [CoordinateDMSData](../../projects/engeapp/app/Data/Location/CoordinateDMSData.php) contém `latitude` e `longitude` mapeados para [DmsValueData](../../projects/engeapp/app/Data/Location/DmsValueData.php).
- **Orientações DMS (Padrão Brasileiro)**:
  - Latitude: `N` (Norte) ou `S` (Sul).
  - Longitude: `L` (Leste) ou `O` (Oeste). **Note que `L` e `O` são usados em vez de `E` e `W`** para alinhar com a terminologia do padrão brasileiro definida em [CoordinateOrientationEnum](../../projects/engeapp/app/Enums/CoordinateOrientationEnum.php).

#### Regras de Conversão no Backend
Para converter DMS (Graus, Minutos, Segundos) em Graus Decimais:
```php
public static function dmsToDecimal(int $degrees, int $minutes, float $seconds, string $orientation): float
{
    $decimal = $degrees + ($minutes / 60.0) + ($seconds / 3600.0);
    if ($orientation === 'S' || $orientation === 'O') {
        $decimal = -$decimal;
    }
    return $decimal;
}
```

### 2. Frontend Vue 3: Integração de Mapa e Reatividade
Ao construir/editar componentes de mapa:
- **Padrão de Componente**: Sempre use Composition API (`<script setup lang="ts">`), SCSS (`<style lang="scss">`) e ordene os blocos: `<template>`, `<script>`, `<style>`.
- **Biblioteca de Mapa**: Use `vue3-google-map`. Carregue-a de forma assíncrona ou renderize condicionalmente usando uma flag de montagem (`isMounted`) para prevenir erros de SSR ou de inicialização.
- **Componente GoogleMap**: Referencie [MaxMaps.vue](../../projects/MaxComponentsUi/src/components/MaxMaps.vue). Todos os atributos no template devem estar em uma única linha.
- **Reatividade e Arraste do Marcador**:
  - Mantenha as coordenadas reativas no componente. Observe (watch) as mudanças de coordenadas e atualize o centro do mapa e a posição do marcador.
  - Vincule o evento `@dragend` no `AdvancedMarker` para capturar as novas coordenadas e atualizar o estado reativo:
    ```ts
    function onDrag(event: any) {
        coordinates.value.latitude = Number(event.latLng.lat().toFixed(7));
        coordinates.value.longitude = Number(event.latLng.lng().toFixed(7));
    }
    ```

### 3. Conversões de Coordenadas no Vue 3 via Proj4
Para converter coordenadas UTM (muito usadas em projetos de usinas solares brasileiras) para Decimal (Latitude/Longitude) no frontend:
- **Configuração do Proj4**: Defina os sistemas de referência de coordenadas (CRS) usando `proj4.defs`.
- **Projeções Brasileiras Comuns**:
  - **SIRGAS 2000 / UTM Zone 23S** (EPSG:31983): `+proj=utm +zone=23 +south +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs`
  - **WGS 84 / UTM Zone 23S** (EPSG:32723): `+proj=utm +zone=23 +south +datum=WGS84 +units=m +no_defs`
- **Exemplo de Conversão**:
  ```typescript
  import proj4 from 'proj4';

  // Define SIRGAS 2000 / UTM Zone 23S e WGS84 (lat/long padrão)
  proj4.defs("EPSG:31983", "+proj=utm +zone=23 +south +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs");

  // Converte UTM (Easting, Northing) para Decimal (Longitude, Latitude)
  // Nota: proj4 retorna [longitude, latitude]
  const [lng, lat] = proj4("EPSG:31983", "WGS84", [easting, northing]);
  ```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NÃO** use orientações `E` (East) ou `W` (West) na formatação DMS brasileira. Use `L` (Leste) e `O` (Oeste).
- **NÃO** duplique regras de validação de coordenadas nos controllers. Sempre delegue a validação de coordenadas às classes Spatie Data (`CoordinateUTMData`, `CoordinateDecimalData`, `CoordinateDMSData`).
- **NÃO** quebre os atributos do template do componente Vue em múltiplas linhas. Mantenha-os em uma única linha.
- **NÃO** use Options API em nenhum componente de mapa/coordenada. Sempre use Composition API com TypeScript.
- **NÃO** escreva estilos inline para alturas ou larguras de mapa. Use estilos SCSS ou classes tailwind (se solicitado).
