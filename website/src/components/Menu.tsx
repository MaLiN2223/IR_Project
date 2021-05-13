import React from 'react';
import { Navbar, Nav, Form, NavDropdown, FormControl, Button } from 'react-bootstrap/'
import SearchPage from './SearchPage';

type MenuProps = {
    links: Array<{ name: string; to: string }>
}


export default class Menu extends React.Component<MenuProps> {
    constructor(props: MenuProps) {
        super(props);
    }
    render() {

        const NavLinks: any = () => this.props.links.map((link: { name: string, to: string }) => <Nav.Link href={link.to}>{link.name}</Nav.Link>)
        return (
            <Navbar bg="dark" variant="dark">
                <Navbar.Brand href="/home">Navbar</Navbar.Brand>
                <Nav className="mr-auto">
                    <NavLinks />
                </Nav>
            </Navbar >
        )
    }
}