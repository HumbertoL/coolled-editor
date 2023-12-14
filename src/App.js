import logo from './logo.svg';
import './App.css';
import { parseData } from './helpers/parse_data';
import Grid from './Grid';


function App() {

  const parsedData = parseData()

  return (
    <div className="App">
      <header className="App-header">
        <Grid binaryString={parsedData} />
      </header>
    </div>
  );
}

export default App;
