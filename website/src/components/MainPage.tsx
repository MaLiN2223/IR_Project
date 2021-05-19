import React, { Component } from "react";
import { BrowserRouter as Router, Route } from "react-router-dom";

import AboutPage from "./AboutPage";
import SearchPage from "./SearchPage";
import Menu from "./Menu";
import Footer from "./Footer";
import HomePage from "./HomePage";

const navigation = {
  links: [
    { name: "Search", to: "/search" },
    { name: "Read me", to: "/about" },
    { name: "Admin", to: "/admin" },
  ],
};

export default class MainPage extends Component<{}, {}> {
  render() {
    const { links } = navigation;
    return (
      <div>
        <Router>
          <div className="App">
            <div>
              <Menu links={links} />
            </div>
            <Route path="/" exact component={HomePage} />
            <Route path="/search" exact component={SearchPage} />
            <Route path="/about" exact component={AboutPage} />
            <Footer />
          </div>
        </Router>
      </div>
    );
  }
}
