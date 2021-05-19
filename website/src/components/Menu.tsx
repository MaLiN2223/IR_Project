import React from "react";
import { Navbar, Nav } from "react-bootstrap/";

type MenuProps = {
  links: Array<{ name: string; to: string }>;
};

export default class Menu extends React.Component<MenuProps> {
  render() {
    const NavLinks: any = () =>
      this.props.links.map((link: { name: string; to: string }) => (
        <Nav.Link href={link.to} key={link.name}>
          {link.name}
        </Nav.Link>
      ));
    return (
      <Navbar bg="dark" variant="dark">
        <Navbar.Brand href="/">Home</Navbar.Brand>
        <Nav className="mr-auto">
          <NavLinks />
        </Nav>
      </Navbar>
    );
  }
}
