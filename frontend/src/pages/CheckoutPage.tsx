import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Button, Container, Typography } from '@mui/material';
import { createCheckoutSession } from '../api/api';

export default function CheckoutPage() {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleCheckout = async () => {
    if (!orderId) return;
    setLoading(true);
    try {
      await createCheckoutSession(Number(orderId));
      setMessage('Pagamento simulado com sucesso! Seu pedido está sendo processado.');
      // After payment, redirect user to their dashboard
      setTimeout(() => navigate('/app/dashboard'), 2000);
    } catch (err) {
      setMessage('Erro ao iniciar pagamento.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Typography variant="h4" gutterBottom>
        Checkout
      </Typography>
      <Typography variant="body1" gutterBottom>
        Clique no botão abaixo para simular o pagamento da sua busca. Uma integração real com o Stripe deve ser implementada para transações ao vivo.
      </Typography>
      <Box sx={{ mt: 4 }}>
        <Button variant="contained" color="primary" onClick={handleCheckout} disabled={loading}>
          {loading ? 'Processando...' : 'Pagar'}
        </Button>
      </Box>
      {message && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          {message}
        </Typography>
      )}
    </Container>
  );
}
