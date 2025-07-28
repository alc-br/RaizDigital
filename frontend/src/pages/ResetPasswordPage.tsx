import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Typography, Box, TextField, Button, Alert } from '@mui/material';
import { resetPassword } from '../api/api';
import { useState } from 'react';

const schema = z.object({
  new_password: z.string().min(6, 'Senha deve ter pelo menos 6 caracteres'),
});

type ResetForm = z.infer<typeof schema>;

export default function ResetPasswordPage() {
  const { token } = useParams();
  const navigate = useNavigate();
  const { register, handleSubmit, formState: { errors } } = useForm<ResetForm>({
    resolver: zodResolver(schema),
  });
  const [message, setMessage] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const onSubmit = async (data: ResetForm) => {
    if (!token) return;
    try {
      const res = await resetPassword(token, data.new_password);
      setMessage(res.detail);
      setErrorMsg(null);
      setTimeout(() => navigate('/login'), 2000);
    } catch (err: any) {
      setErrorMsg(err?.response?.data?.detail || 'Erro ao redefinir senha');
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Typography variant="h4" gutterBottom>Redefinir Senha</Typography>
      {message && <Alert severity="success">{message}</Alert>}
      {errorMsg && <Alert severity="error">{errorMsg}</Alert>}
      <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ mt: 2, display:'flex', flexDirection:'column', gap:2 }}>
        <TextField
          label="Nova Senha"
          type="password"
          {...register('new_password')}
          error={!!errors.new_password}
          helperText={errors.new_password?.message}
        />
        <Button type="submit" variant="contained">Salvar</Button>
      </Box>
    </Container>
  );
}
