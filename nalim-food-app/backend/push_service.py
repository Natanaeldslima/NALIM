import os
import json
import logging
import threading
import datetime
from typing import Optional, Dict, Any, List
from database import SessionLocal
from models import PushSubscription

logger = logging.getLogger("nalim.push")

# =====================================================================
# CONFIGURAÇÃO DE CHAVES VAPID (WEB PUSH RFC 8291 / 8292)
# =====================================================================
# Se configurado no Render / Environment, usa as variáveis do usuário.
# Caso contrário, utiliza par de chaves ECDSA P-256 válido gerado de fábrica,
# garantindo funcionamento imediato "out-of-the-box" sem erros de inicialização.

DEFAULT_VAPID_PUBLIC_KEY = "BPd9wwsaSAiyZh988WSKrGsHepD73mAOxfiwlR4MMRVHk7-vfzcnWpTfKjKuihdJqPsZkVhOl1bm2JuowQPvYes"
DEFAULT_VAPID_PRIVATE_KEY = "FT8wjHjKDFf7JLjR-ogA3B_2LaQlWHsvshINjjgfb-Q"
DEFAULT_VAPID_EMAIL = "contato@nalim.com.br"

VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", DEFAULT_VAPID_PUBLIC_KEY).strip()
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", DEFAULT_VAPID_PRIVATE_KEY).strip()
VAPID_EMAIL = os.getenv("VAPID_EMAIL", DEFAULT_VAPID_EMAIL).strip()

def get_vapid_claims() -> Dict[str, str]:
    email = os.getenv("VAPID_EMAIL", DEFAULT_VAPID_EMAIL).strip()
    return {"sub": f"mailto:{email}"}

def salvar_subscription(garcom_id: str, subscription_dict: Dict[str, Any]) -> bool:
    """Salva ou atualiza uma inscrição Web Push no banco de dados."""
    if not subscription_dict or not isinstance(subscription_dict, dict):
        return False
    endpoint = subscription_dict.get("endpoint")
    if not endpoint:
        return False

    db = SessionLocal()
    try:
        sub_str = json.dumps(subscription_dict)
        registro = db.query(PushSubscription).filter(PushSubscription.endpoint == endpoint).first()
        if registro:
            registro.garcom_id = garcom_id or "garcom"
            registro.subscription_json = sub_str
            registro.criado_em = datetime.datetime.utcnow()
        else:
            novo = PushSubscription(
                garcom_id=garcom_id or "garcom",
                endpoint=endpoint,
                subscription_json=sub_str,
                criado_em=datetime.datetime.utcnow()
            )
            db.add(novo)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"[PUSH] Erro ao salvar push subscription: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def remover_subscription_por_endpoint(endpoint: str):
    """Remove inscrição expirada (código 404/410 do FCM/Mozilla Push Service)."""
    db = SessionLocal()
    try:
        db.query(PushSubscription).filter(PushSubscription.endpoint == endpoint).delete()
        db.commit()
    except Exception as e:
        logger.warning(f"[PUSH] Falha ao remover subscription expirada: {e}")
        db.rollback()
    finally:
        db.close()

def listar_todas_subscriptions() -> List[Dict[str, Any]]:
    """Recupera todas as inscrições ativas gravadas no banco de dados."""
    db = SessionLocal()
    resultado = []
    try:
        subs = db.query(PushSubscription).all()
        for s in subs:
            try:
                info = json.loads(s.subscription_json)
                resultado.append({
                    "id": s.id,
                    "garcom_id": s.garcom_id,
                    "endpoint": s.endpoint,
                    "subscription_info": info
                })
            except Exception:
                pass
    except Exception as e:
        logger.error(f"[PUSH] Erro ao listar subscriptions: {e}")
    finally:
        db.close()
    return resultado

def _enviar_push_worker(payload: Dict[str, Any], garcom_filtro: Optional[str] = None):
    """Executa o envio do push em thread separada com proteção de falhas."""
    try:
        from pywebpush import webpush, WebPushException
    except ImportError:
        logger.warning("[PUSH] Biblioteca pywebpush não encontrada neste ambiente. Pulando envio push.")
        return

    subscriptions = listar_todas_subscriptions()
    if not subscriptions:
        return

    claims = get_vapid_claims()
    priv_key = os.getenv("VAPID_PRIVATE_KEY", DEFAULT_VAPID_PRIVATE_KEY).strip()

    data_json = json.dumps(payload)

    for sub in subscriptions:
        # Se for especificado um garçom específico e ele tiver inscrição própria, prioriza.
        # Caso contrário, notifica todos os aparelhos ativos da equipe.
        endpoint = sub.get("endpoint")
        sub_info = sub.get("subscription_info")
        if not sub_info or not endpoint:
            continue

        try:
            webpush(
                subscription_info=sub_info,
                data=data_json,
                vapid_private_key=priv_key,
                vapid_claims=claims
            )
        except WebPushException as ex:
            if ex.response is not None and ex.response.status_code in (404, 410):
                # Inscrição desativada ou aparelho removeu permissão
                remover_subscription_por_endpoint(endpoint)
            else:
                logger.warning(f"[PUSH] Erro no WebPushException para {endpoint[:40]}...: {ex}")
        except Exception as ex:
            logger.warning(f"[PUSH] Erro genérico ao enviar webpush: {ex}")

def notificar_garcom_push(mesa: str, comanda_num: Any, solicitante: Optional[str] = None):
    """
    Dispara notificação push para os celulares dos garçons informando que o pedido está pronto.
    Roda em thread daemon para garantir resposta ultra-rápida na cozinha do KDS.
    """
    payload = {
        "titulo": f"🔔 Pedido Pronto: {mesa}!",
        "corpo": f"Ticket #{comanda_num} pronto na chapa p/ recolher e servir.",
        "tag": f"pedido-{comanda_num}",
        "url": "/garcom",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    threading.Thread(target=_enviar_push_worker, args=(payload, solicitante), daemon=True).start()

def enviar_push_teste(garcom_id: str = "Garçom"):
    """Dispara um push de teste imediato para validar som e alerta no celular."""
    payload = {
        "titulo": "🔔 Notificações Ativadas!",
        "corpo": f"Tudo pronto, {garcom_id}! Você receberá alertas mesmo com a tela bloqueada.",
        "tag": "teste-push",
        "url": "/garcom"
    }
    threading.Thread(target=_enviar_push_worker, args=(payload, None), daemon=True).start()
