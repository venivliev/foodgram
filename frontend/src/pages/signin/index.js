import { Container, Input, Title, Main, Form, Button } from '../../components'
import styles from './styles.module.css'
import { useFormWithValidation } from '../../utils'
import { AuthContext } from '../../contexts'
import { Redirect } from 'react-router-dom'
import { useContext } from 'react'
import { Helmet } from 'react-helmet'

const SignIn = ({ onSignIn }) => {
  const { values, handleChange, errors, isValid, resetForm } = useFormWithValidation()
  const authContext = useContext(AuthContext)

  return <Main>
    {authContext && <Redirect to='/recipes' />}
    <Container>
      <Helmet>
        <title>Войти на сайт</title>
        <meta name="description" content="ФудГрам - Войти на сайт" />
        <meta property="og:title" content="Войти на сайт" />
      </Helmet>
      <Title title='Войти на сайт' />
      <Form
        className={styles.form}
        onSubmit={e => {
          e.preventDefault()
          onSignIn(values)
        }}
      >
        <Input
          required
          label='Электронная почта'
          name='email'
          onChange={handleChange}
        />
        <Input
          required
          label='Пароль'
          type='password'
          name='password'
          onChange={handleChange}
        />
        <Button
          modifier='style_dark-blue'
          disabled={!isValid}
          type='submit'
          className={styles.button}
        >
          Войти
        </Button>
      </Form>
    </Container>
  </Main>
}

export default SignIn
