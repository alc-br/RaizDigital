import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useSearchParams, useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  TextField,
  Button,
  Alert,
  Link,
} from '@mui/material';
import { loginUser } from '../api/api';
import { useAuthStore } from '../store/useAuthStore';
import { useState } from 'react';

const loginSchema = z.object({
  email: z.string().email('E-mail inválido'),
  password: z.string().min(6, 'Senha é obrigatória'),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });
  const setTokens = useAuthStore((s) => s.setTokens);
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const onSubmit = async (data: LoginForm) => {
    try {
      const res = await loginUser(data.email, data.password);
      setTokens(res.access_token, res.refresh_token);
      const next = params.get('next') || '/app/dashboard';
      navigate(next);
    } catch (err: any) {
      setErrorMsg(err?.response?.data?.detail || 'Falha no login');
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Typography variant="h4" gutterBottom>Entrar</Typography>
      {errorMsg && <Alert severity="error">{errorMsg}</Alert>}
      <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ mt: 2, display:'flex', flexDirection:'column', gap:2 }}>
        <TextField
          label="E-mail"
          {...register('email')}
          error={!!errors.email}
          helperText={errors.email?.message}
        />
        <TextField
          label="Senha"
          type="password"
          {...register('password')}
          error={!!errors.password}
          helperText={errors.password?.message}
        />
        <Button type="submit" variant="contained">Entrar</Button>
        <Link component={RouterLink} to="/esqueci-senha">Esqueci minha senha</Link>
        <Link component={RouterLink} to="/cadastro">Não tem conta? Cadastre-se</Link>
      </Box>
    </Container>
  );
}
