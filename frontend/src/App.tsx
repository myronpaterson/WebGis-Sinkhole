// Importamos os "superpoderes" do React que vamos usar
import { useState, useEffect } from 'react';
// Importamos os componentes do mapa, incluindo o novo GeoJSON
import { MapContainer, TileLayer, GeoJSON, Popup } from 'react-leaflet';

// 1. Definimos o "formato" ou a "estrutura" dos dados de cada medição.
//    Isso ajuda o TypeScript a entender nossos dados e evitar erros.
type MedicaoType = {
  id: number;
  id_relatorio: string;
  data_medicao: string;
  area_m2: number;
  perimetro_m: number;
  diametro_externo_maior_m: number;
  diametro_externo_menor_m: number;
  geometria_geojson: string; // A geometria vem como um texto GeoJSON
};

function App() {
  // 2. Criamos nossa "caixa de memória" com o hook useState.
  //    Ela se chama 'medicoes' e começa como uma lista vazia [].
  const [medicoes, setMedicoes] = useState<MedicaoType[]>([]);
  const position: [number, number] = [-13.0126, -38.7564]; // Posição inicial do mapa

  // 3. Usamos o "gatilho" useEffect para buscar os dados da API.
  //    O `[]` no final significa: "rode este código apenas uma vez, quando a página carregar".
  useEffect(() => {
    // A função 'fetch' é a forma padrão de fazer requisições na web.
    // Estamos pedindo os dados do nosso backend.
    fetch('http://127.0.0.1:8000/medicoes')
      .then(response => response.json()) // Quando a resposta chegar, transforme-a em JSON
      .then(data => setMedicoes(data)); // Quando o JSON estiver pronto, guarde os dados na nossa "caixa" de memória.
  }, []);

  return (
    <MapContainer center={position} zoom={16} className="map-container">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* 4. Agora, fazemos um "loop" na nossa memória. */}
      {/* Para cada 'medicao' na lista 'medicoes', desenhe um componente GeoJSON. */}
      {medicoes.map(medicao => (
        // O componente GeoJSON é inteligente. Ele sabe como ler o formato GeoJSON.
        // Precisamos usar JSON.parse() para transformar o texto da geometria em um objeto que ele entenda.
        <GeoJSON key={medicao.id} data={JSON.parse(medicao.geometria_geojson)}>
          <Popup>
            <div>
              <h3>{medicao.id_relatorio}</h3>
              <p>Data: {medicao.data_medicao}</p>
              <p>Área: {medicao.area_m2} m²</p>
              <p>Perímetro: {medicao.perimetro_m} m</p>
            </div>
          </Popup>
        </GeoJSON>
      ))}
    </MapContainer>
  );
}

export default App;