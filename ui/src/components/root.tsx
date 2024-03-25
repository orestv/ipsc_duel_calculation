import React from "react";
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import {NavLink, Outlet} from 'react-router-dom';


export function DuelNavbar() {
    return (
        <Navbar expand="sm" className="bg-body-tertiary">
            <Container>
                <Navbar.Brand>
                    <h1>Дуелі</h1>
                </Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav"/>
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="me-auto">
                        <Nav.Link as={NavLink} to="/duels">Дуелі</Nav.Link >
                        <Nav.Link as={NavLink} to="/matches">Матчі</Nav.Link >
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    )
}

export function RootComponent(){
    return (
        <>
            <DuelNavbar/>
            <Container>
                <Outlet/>
            </Container>
        </>
    )
}