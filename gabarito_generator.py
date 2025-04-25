import os
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from contextlib import suppress

# CONFIGS
PDF_OUTPUT_DIR = "output/pdf"
QR_OUTPUT_DIR = "output/qr"
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 50
BUBBLE_SPACING = 21  # AJUSTA ESPAÇAMENTO ENTRE BOLINHAS
FONT_SIZE = 12
BUBBLE_SIZE = 15
HORIZONTAL_SPACING = 18  # AJUSTA ESPAÇAMENTO ENTRE BOLINHAS

# Configurações para múltiplas colunas
MAX_QUESTOES_POR_COLUNA = 30
MAX_COLUNAS = 4
COLUNA_SPACING = 130  # Espaçamento entre colunas

def gerar_qr_code(gabarito_id):
    qr_path = os.path.join(QR_OUTPUT_DIR, f"{gabarito_id}.png")
    qr = qrcode.make(gabarito_id)
    qr.save(qr_path)
    return qr_path

def gerar_pdf(gabarito_id, disciplina, turma, num_questoes, alternativas, questoes_por_coluna=None, num_colunas=None):
    """
    Gera um PDF de gabarito com múltiplas colunas.
    
    Parâmetros:
    - gabarito_id: Identificador único do gabarito
    - disciplina: Nome da disciplina
    - turma: Identificação da turma
    - num_questoes: Número total de questões
    - alternativas: Lista de alternativas (ex: ["A", "B", "C", "D", "E"])
    - questoes_por_coluna: Número de questões por coluna (opcional, padrão é MAX_QUESTOES_POR_COLUNA)
    - num_colunas: Número de colunas (opcional, padrão é MAX_COLUNAS)
    """
    # Definir valores padrão se não forem fornecidos
    questoes_por_coluna = questoes_por_coluna or MAX_QUESTOES_POR_COLUNA
    num_colunas = num_colunas or MAX_COLUNAS
    
    os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)
    os.makedirs(QR_OUTPUT_DIR, exist_ok=True)

    pdf_path = os.path.join(PDF_OUTPUT_DIR, f"{gabarito_id}.pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)

    # Header
    c.setFont("Helvetica-Bold", 12)  # Define a fonte como Helvetica em negrito, tamanho 10
    c.drawString(MARGIN + 0, PAGE_HEIGHT - MARGIN, f"Disciplina: {disciplina}")  # Desenha o texto da disciplina no topo da página
    c.drawString(MARGIN + 150, PAGE_HEIGHT - MARGIN, f"Turma: {turma}")  # Desenha o texto da turma no topo da página, à direita
    c.setFont("Helvetica", 12)  # Muda a fonte para Helvetica normal (sem negrito), mantendo tamanho 10
    c.drawString(MARGIN + 0, PAGE_HEIGHT - MARGIN - 20, "Nome:___________________________")  # Desenha o campo para nome do aluno
    #c.drawString(MARGIN + 0, PAGE_HEIGHT - MARGIN - 40, "Assinatura:_______________________")  # Desenha o campo para assinatura

    # QR Code
    qr_path = gerar_qr_code(gabarito_id)
    c.drawImage(qr_path, MARGIN + 435, PAGE_HEIGHT - MARGIN - 45, width=80, height=80)  # Ajustado para ficar ao lado da turma

    # Questões
    start_y = PAGE_HEIGHT - MARGIN - 60
    c.setFont("Helvetica", FONT_SIZE)
    
    # Limitar o número de questões ao máximo suportado
    max_questoes_total = questoes_por_coluna * num_colunas
    num_questoes = min(num_questoes, max_questoes_total)
    
    # Calcular número de colunas necessárias
    num_colunas_necessarias = min((num_questoes + questoes_por_coluna - 1) // questoes_por_coluna, num_colunas)
    
    for i in range(num_questoes):
        # Determinar em qual coluna a questão deve ser colocada
        coluna = i // questoes_por_coluna
        posicao_na_coluna = i % questoes_por_coluna
        
        # Calcular posição x e y
        x_offset = coluna * COLUNA_SPACING
        y = start_y - (posicao_na_coluna * BUBBLE_SPACING)
        
        # Se a posição y for muito baixa, criar nova página
        if y < 100 and posicao_na_coluna == 0 and coluna == 0:
            c.showPage()
            y = PAGE_HEIGHT - MARGIN
            start_y = y
        
        questao = f"{i+1:02d}"
        c.drawString(MARGIN + x_offset, y, f"{questao}-")
        
        for idx, alt in enumerate(alternativas):
            x = MARGIN + 35 + x_offset + (idx * HORIZONTAL_SPACING)  # AJUSTA ESPAÇAMENTO ENTRE BOLAS E QUESTÕES
            c.circle(x, y + 5, BUBBLE_SIZE / 2)

            # Centraliza a letra dentro do círculo
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(x, y + 1, alt)
            c.setFont("Helvetica", FONT_SIZE)  # Restaura a fonte para o tamanho padrão

    c.save()
    print(f"[✓] PDF gerado: {pdf_path}")
    return pdf_path

# Exemplo de uso
if __name__ == "__main__":
    id_gabarito = "GAB-001-MAT-3A"
    gerar_pdf(
        gabarito_id=id_gabarito,
        disciplina="Matemática",
        turma="3A",
        num_questoes=40,  # Número total de questões
        alternativas=["A", "B", "C", "D", "E"],
        questoes_por_coluna=10,  # Personalização: questões por coluna
        num_colunas=4  # Personalização: número de colunas
    )
