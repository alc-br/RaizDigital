import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  TextField,
  Button,
  Alert,
  Link,
} from '@mui/material';
import { registerUser, loginUser } from '../api/api';
import { useAuthStore } from '../store/useAuthStore';
import { useState } from 'react';

const registerSchema = z.object({
  full_name: z.string().min(3, 'Nome obrigatório'),
  email: z.string().email('E-mail inválido'),
  password: z.string().min(6, 'Senha deve ter pelo menos 6 caracteres'),
});

type RegisterForm = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const { register, handleSubmit, formState: { errors } } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
  });
  const setTokens = useAuthStore((s) => s.setTokens);
  const navigate = useNavigate();
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const onSubmit = async (data: RegisterForm) => {
    try {
      await registerUser({ email: data.email, full_name: data.full_name, password: data.password });
      const res = await loginUser(data.email, data.password);
      setTokens(res.access_token, res.refresh_token);
      navigate('/app/dashboard');
    } catch (err: any) {
      setErrorMsg(err?.response?.data?.detail || 'Erro ao criar conta');
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Typography variant="h4" gutterBottom>Criar Conta</Typography>
      {errorMsg && <Alert severity="error">{errorMsg}</Alert>}
      <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ mt: 2, display:'flex', flexDirection:'column', gap:2 }}>
        <TextField
          label="Nome Completo"
          {...register('full_name')}
          error={!!errors.full_name}
          helperText={errors.full_name?.message}
        />
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
        <Button type="submit" variant="contained">Registrar</Button>
        <Link component={RouterLink} to="/login">Já tem conta? Entrar</Link>
      </Box>
    </Container>
  );
}
