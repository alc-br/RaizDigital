import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { Container, Typography, Box, TextField, Button, Alert } from '@mui/material';
import { forgotPassword } from '../api/api';
import { useState } from 'react';

const schema = z.object({
  email: z.string().email('E-mail inválido'),
});

type ForgotPasswordForm = z.infer<typeof schema>;

export default function ForgotPasswordPage() {
  const { register, handleSubmit, formState: { errors } } = useForm<ForgotPasswordForm>({
    resolver: zodResolver(schema),
  });
  const [message, setMessage] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const onSubmit = async (data: ForgotPasswordForm) => {
    try {
      const res = await forgotPassword(data.email);
      setMessage(res.detail);
      setErrorMsg(null);
    } catch (err: any) {
      setErrorMsg('Erro ao enviar e-mail');
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Typography variant="h4" gutterBottom>Recuperar Senha</Typography>
      {message && <Alert severity="success">{message}</Alert>}
      {errorMsg && <Alert severity="error">{errorMsg}</Alert>}
      <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ mt: 2, display:'flex', flexDirection:'column', gap:2 }}>
        <TextField
          label="E-mail"
          {...register('email')}
          error={!!errors.email}
          helperText={errors.email?.message}
        />
        <Button type="submit" variant="contained">Enviar</Button>
      </Box>
    </Container>
  );
}
