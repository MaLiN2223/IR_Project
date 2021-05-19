import axios from "axios";
import React, { Component } from "react";
import { baseUrl } from "../consts";
import "../styles/footer.css";

type FooterState = {
  version: string;
};

const versionUrl = baseUrl + "metadata/version";

export default class Footer extends Component<{}, FooterState> {
  constructor(props: Readonly<any>) {
    super(props);
    this.state = { version: "unknown" };
  }
  private async refreshVersion(): Promise<boolean> {
    axios
      .get<string>(versionUrl)
      .then((response) => {
        this.setState({ version: response.data });
      })
      .catch((x) => {
        this.setState({ version: "unable to retrieve the version" });
      });
    return true;
  }

  componentDidMount() {
    this.refreshVersion();
  }

  render() {
    console.log(
      `${process.env.REACT_APP_NAME} ${process.env.REACT_APP_CURRENT_GIT_SHA}`
    );
    return (
      <footer className="footer">
        VERSION: backend {this.state.version} | fontend{" "}
        {process.env.REACT_APP_CURRENT_GIT_SHA}
        <p style={{ fontSize: "7px", textAlign: "center" }}>
          Empire did nothing wrong. Long live the Empire!
        </p>
      </footer>
    );
  }
}
