import { useEffect, useState } from 'react';
import { Container, Typography, Box, TextField, Button, Alert } from '@mui/material';
import { getCurrentUser, updateProfile } from '../api/api';

interface UserProfile {
  id: number;
  email: string;
  full_name?: string;
  created_at: string;
}

export default function ProfilePage() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const data = await getCurrentUser();
        setUser(data);
        setName(data.full_name || '');
        setEmail(data.email);
      } catch (err) {
        setErrorMsg('Erro ao carregar perfil');
      }
    })();
  }, []);

  const handleProfileUpdate = async () => {
    try {
      await updateProfile({ full_name: name, email });
      setMessage('Perfil atualizado com sucesso');
      setErrorMsg(null);
    } catch (err: any) {
      setErrorMsg(err?.response?.data?.detail || 'Erro ao atualizar perfil');
    }
  };

  const handlePasswordChange = async () => {
    if (newPassword !== confirmPassword) {
      setErrorMsg('As senhas não conferem');
      return;
    }
    try {
      await updateProfile({ current_password: currentPassword, new_password: newPassword });
      setMessage('Senha alterada com sucesso');
      setErrorMsg(null);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      setErrorMsg(err?.response?.data?.detail || 'Erro ao alterar senha');
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Typography variant="h4" gutterBottom>Meu Perfil</Typography>
      {message && <Alert severity="success">{message}</Alert>}
      {errorMsg && <Alert severity="error">{errorMsg}</Alert>}
      {user && (
        <>
          <Box sx={{ mt: 2, display:'flex', flexDirection:'column', gap:2 }}>
            <Typography variant="h6">Informações Pessoais</Typography>
            <TextField
              label="Nome Completo"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            <TextField
              label="E-mail"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <Button variant="contained" onClick={handleProfileUpdate}>Salvar</Button>
          </Box>
          <Box sx={{ mt: 4, display:'flex', flexDirection:'column', gap:2 }}>
            <Typography variant="h6">Alterar Senha</Typography>
            <TextField
              label="Senha Atual"
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
            />
            <TextField
              label="Nova Senha"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
            />
            <TextField
              label="Confirmar Nova Senha"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
            <Button variant="contained" onClick={handlePasswordChange}>Alterar Senha</Button>
          </Box>
        </>
      )}
    </Container>
  );
}
