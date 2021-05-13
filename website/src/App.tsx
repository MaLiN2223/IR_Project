import './App.css';
import { BrowserRouter as Router, Route, Link } from "react-router-dom";

import AboutPage from './components/AboutPage'
import SearchPage from './components/SearchPage';
import Menu from './components/Menu';
import '../node_modules/bootstrap/dist/css/bootstrap.min.css';
import HomePage from './components/HomePage';

const navigation = {
    links: [
        { name: "Home", to: "/home" },
        { name: "Retrieval", to: "/search" },
        { name: "Read me", to: "/about" },
        { name: "Admin", to: "/admin" },
    ]
}

 
function App() {
    const { links } = navigation;
    return (
        <div>
            <Router>
                <div className="App">
                    <div>
                        <Menu links={links} />
                    </div>
                    <Route path="/home" exact component={HomePage} />
                    <Route path="/search" exact component={SearchPage} />
                    <Route path="/about" exact component={AboutPage} />
                </div>

            </Router>
        </div>
    );
}

export default App;
