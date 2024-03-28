import React, {useRef} from "react";
import {Button, Form, InputGroup, Modal} from "react-bootstrap";
import {FaCircle} from "react-icons/fa";
import Container from "react-bootstrap/Container";

export interface MatchCreateModalProps {
    show: boolean
    onHide: (submitted: boolean, result?: MatchCreateResult) => void
}

export interface MatchCreateResult {
    name: string
}

export default function MatchCreateModal(props: MatchCreateModalProps) {
    const formRef = useRef(null)
    const nameRef = useRef(null)
    const handleSubmit = async (event: any) => {
        event.preventDefault()
        const formData = new FormData(formRef.current)
        const formDataObj = Object.fromEntries(formData.entries()) as {[key: string]: string}
        props.onHide(
            true,
            {name: formDataObj["name"]}
        )
    }

    const handleGenerateName = () => {
        nameRef.current.value = new Date().toLocaleString("uk-UA", {hour12: false})
    }

    return (
        <Modal show={props.show} onHide={() => {props.onHide(false)}}>
            <Form
                ref={formRef}
                onSubmit={handleSubmit}
            >
            <Modal.Header closeButton>
                <Modal.Title>Створити матч</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <Form.Group>
                    <Form.Label>Назва матчу</Form.Label>
                    <InputGroup className={"mb-3"}>
                        <Form.Control
                            ref={nameRef}
                            name={"name"}
                            type={"text"}
                            aria-describedby={"button-generate-name"}
                            required
                        />
                        <Button
                            id={"button-generate-name"}
                            variant={"outline-primary"}
                            onClick={handleGenerateName}
                        >
                            Згенерувати
                        </Button>
                    </InputGroup>
                </Form.Group>
            </Modal.Body>
            <Modal.Footer className={"d-flex justify-content-between"}>
                <Button
                    variant={"outline-dark"}
                    onClick={() => {props.onHide(false)}}
                >
                    Закрити
                </Button>
                <Button type={"submit"} variant={"primary"}>Створити</Button>
            </Modal.Footer>
            </Form>
        </Modal>
    )
}