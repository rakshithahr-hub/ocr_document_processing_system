import React from 'react';
import { Navbar as BSNavbar, Container, Nav } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FaCamera } from 'react-icons/fa';

function Navbar() {
  return (
    <BSNavbar bg="primary" variant="dark" expand="lg" className="shadow-sm">
      <Container>
        <BSNavbar.Brand as={Link} to="/" className="d-flex align-items-center">
          <FaCamera className="me-2" size={24} />
          <span className="fw-bold">OCR Pro</span>
        </BSNavbar.Brand>
        <BSNavbar.Toggle aria-controls="basic-navbar-nav" />
        <BSNavbar.Collapse id="basic-navbar-nav">
          <Nav className="ms-auto">
            <Nav.Link as={Link} to="/">Home</Nav.Link>
            <Nav.Link as={Link} to="/about">About OCR</Nav.Link>
          </Nav>
        </BSNavbar.Collapse>
      </Container>
    </BSNavbar>
  );
}

export default Navbar;