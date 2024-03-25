import React from "react";
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import {NavLink, Outlet} from 'react-router-dom';


export function RootNavbar() {
    return (
        <Navbar className="bg-body-secondary mb-4">
            <Container>
                <Navbar.Brand>
                    <h1>Дуелі</h1>
                </Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav"/>
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav variant={"underline"} className="me-auto">
                        <Nav.Item>
                            <Nav.Link as={NavLink} to="/duels">Планування</Nav.Link >
                        </Nav.Item>
                        <Nav.Item>
                            <Nav.Link as={NavLink} to="/matches">Суддівство</Nav.Link >
                        </Nav.Item>
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    )
}

export function RootComponent(){
    return (
        <>
            <RootNavbar/>
            <Outlet/>
        </>
    )
}