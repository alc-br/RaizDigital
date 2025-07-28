import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  TextField,
  Typography,
  Alert,
} from '@mui/material';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { createOrder } from '../api/api';
import { useAuthStore } from '../store/useAuthStore';

const orderSchema = z.object({
  target_name: z.string().min(3, 'Nome é obrigatório'),
  target_dob_approx: z.string().optional(),
  target_city: z.string().optional(),
  target_state: z.string().optional(),
  target_parents_names: z.string().optional(),
  additional_info: z.string().optional(),
});

type OrderFormData = z.infer<typeof orderSchema>;

export default function NewOrderPage() {
  const navigate = useNavigate();
  const token = useAuthStore((s) => s.token);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<OrderFormData>({
    resolver: zodResolver(orderSchema),
  });

  const onSubmit = async (data: OrderFormData) => {
    try {
      const price = 100.0; // placeholder price
      const order = await createOrder({ ...data, order_price: price });
      navigate(`/checkout/${order.id}`);
    } catch (err: any) {
      setErrorMsg(err?.response?.data?.detail || 'Erro ao criar pedido');
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Typography variant="h4" gutterBottom>
        Novo Pedido
      </Typography>
      {errorMsg && <Alert severity="error">{errorMsg}</Alert>}
      <Box component="form" noValidate onSubmit={handleSubmit(onSubmit)} sx={{ mt: 2, display:'flex', flexDirection:'column', gap:2 }}>
        <TextField
          label="Nome do Antepassado"
          {...register('target_name')}
          error={!!errors.target_name}
          helperText={errors.target_name?.message}
          required
        />
        <TextField
          label="Data de Nascimento (aprox.)"
          {...register('target_dob_approx')}
        />
        <TextField
          label="Cidade"
          {...register('target_city')}
        />
        <TextField
          label="Estado"
          {...register('target_state')}
        />
        <TextField
          label="Nome dos Pais"
          {...register('target_parents_names')}
        />
        <TextField
          label="Informações Adicionais"
          {...register('additional_info')}
          multiline
          rows={3}
        />
        <Button type="submit" variant="contained" color="primary">
          Prosseguir para Pagamento
        </Button>
      </Box>
    </Container>
  );
}
