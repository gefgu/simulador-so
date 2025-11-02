import subprocess
from datetime import datetime
from PIL import ImageGrab, Image  # type: ignore

def convert_ps_to_png(ps_file, png_file):
    """Converte PS/EPS para PNG usando ImageMagick."""
    try:
        # Tenta diferentes comandos do ImageMagick
        commands = [
            ['convert', ps_file, png_file],
            ['magick', ps_file, png_file],  # ImageMagick 7+
        ]
        
        for cmd in commands:
            try:
                result = subprocess.run(cmd, 
                                        capture_output=True, 
                                        text=True, 
                                        timeout=30,
                                        check=True)
                print(f"✅ Conversão ImageMagick bem-sucedida: {png_file}")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                continue
                
        print("⚠️ ImageMagick não encontrado ou falhou")
        return False
        
    except Exception as e:
        print(f"⚠️ Erro na conversão ImageMagick: {e}")
        return False

def convert_ps_to_png_pillow(ps_file, png_file):
    """Converte PS/EPS para PNG usando Pillow (fallback)."""
    try:
        print("🔄 Tentando conversão com Pillow...")
        
        # Pillow pode abrir EPS se Ghostscript estiver disponível
        with Image.open(ps_file) as img:
            # Converte para RGB se necessário
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(png_file, 'PNG', dpi=(300, 300))
            print(f"✅ Conversão Pillow bem-sucedida: {png_file}")
            return True
            
    except Exception as e:
        print(f"⚠️ Conversão Pillow falhou: {e}")
        print("💡 Para habilitar: sudo apt install ghostscript (Linux)")
        return False

def convert_ps_to_png_with_white_bg(ps_file, png_file):
    """Converte PS/EPS para PNG com fundo branco usando ImageMagick."""
    try:
        # Comandos com fundo branco forçado
        commands = [
            ['convert', '-background', 'white', '-flatten', ps_file, png_file],
            ['magick', '-background', 'white', '-flatten', ps_file, png_file],  # ImageMagick 7+
        ]
        
        for cmd in commands:
            try:
                result = subprocess.run(cmd, 
                                        capture_output=True, 
                                        text=True, 
                                        timeout=30,
                                        check=True)
                print(f"✅ Conversão com fundo branco bem-sucedida: {png_file}")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                continue
                
        print("⚠️ ImageMagick não encontrado ou falhou (fundo branco)")
        return False
        
    except Exception as e:
        print(f"⚠️ Erro na conversão com fundo branco: {e}")
        return False

def convert_ps_to_png_pillow_with_white_bg(ps_file, png_file):
    """Converte PS/EPS para PNG com fundo branco usando Pillow."""
    try:
        print("🔄 Tentando conversão com fundo branco usando Pillow...")
        
        with Image.open(ps_file) as img:
            # Cria uma imagem com fundo branco
            if img.mode == 'RGBA':
                # Para imagens com transparência, compõe sobre fundo branco
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])  # usa canal alpha como máscara
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            img.save(png_file, 'PNG', dpi=(300, 300))
            print(f"✅ Conversão com fundo branco Pillow bem-sucedida: {png_file}")
            return True
            
    except Exception as e:
        print(f"⚠️ Erro na conversão Pillow com fundo branco: {e}")
        return False