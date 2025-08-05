import { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { Box, Button, Container, Typography, Alert } from '@mui/material';
import { createCheckoutSession } from '../api/api';

export default function CheckoutPage() {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Exibe uma mensagem se o usuário cancelar o pagamento no Stripe
  useEffect(() => {
    if (searchParams.get('payment') === 'cancelled') {
      setErrorMsg('O pagamento foi cancelado. Você pode tentar novamente a qualquer momento.');
    }
  }, [searchParams]);

  const handleCheckout = async () => {
    if (!orderId) return;
    setLoading(true);
    setErrorMsg(null);
    try {
      // A API retorna um objeto com a URL de checkout do Stripe
      const session = await createCheckoutSession(Number(orderId));
      if (session && session.url) {
        // CORREÇÃO: Redireciona o usuário para a página de pagamento do Stripe
        window.location.href = session.url;
      } else {
        setErrorMsg('Não foi possível obter a URL de pagamento.');
      }
    } catch (err: any) {
      setErrorMsg(err?.response?.data?.detail || 'Erro ao iniciar pagamento.');
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
        Você será redirecionado para um ambiente seguro para concluir o pagamento.
      </Typography>
      {errorMsg && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {errorMsg}
        </Alert>
      )}
      <Box sx={{ mt: 4 }}>
        <Button variant="contained" color="primary" onClick={handleCheckout} disabled={loading}>
          {loading ? 'Processando...' : `Pagar Pedido #${orderId}`}
        </Button>
      </Box>
    </Container>
  );
}