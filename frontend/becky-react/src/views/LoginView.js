import React from "react";
import { Button, InputGroup, Form } from "react-bootstrap";

class LoginView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            username: '',
            password: '',
        }

        this.login = this.login.bind(this);
    }


    login(event) {
        event.preventDefault();
        console.log(this.state);
        fetch("http://localhost:6701/api/login/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": this.props.csrf,
            },
            credentials: "include",
            body: JSON.stringify({username: this.state.username, password: this.state.password}),
        })
        .then((res) => res.json())
        .then((data) => {
          this.props.setAuthenticated(true);
        })
        .catch((err) => {
          console.log(err);
        });
    }


    render() {
        return (
            <div>
                <Form onSubmit={this.login}>
                    <Form.Group controlId="formUsername">
                        <Form.Label> Username: </Form.Label>
                        <Form.Control type="username" placeholder="Enter username" onChange={e =>  this.setState({username: e.target.value})}/>
                    </Form.Group>
                    <Form.Group controlId="formPassword">
                        <Form.Label> Password: </Form.Label>
                        <Form.Control type="password" placeholder="Enter password" onChange={e => this.setState({password: e.target.value})}/>
                    </Form.Group>
                    <Button variant="primary" type="submit">
                        Submit
                    </Button>
                </Form>
            </div>
        );
    }
}

export default LoginView;
