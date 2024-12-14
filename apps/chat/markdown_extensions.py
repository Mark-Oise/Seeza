import markdown
from markdown.preprocessors import Preprocessor
from django.template.loader import render_to_string

class CodeBlockPreprocessor(Preprocessor):
    def __init__(self, message_id):
        self.message_id = message_id
        self.block_counter = 0

    def run(self, lines):
        new_lines = []
        in_code_block = False
        code_block_lines = []
        language = ''

        for line in lines:
            if line.strip().startswith('```'):
                if in_code_block:
                    # End of code block
                    code = '\n'.join(code_block_lines)
                    rendered_block = render_to_string('chat/partials/code_block.html', {
                        'message_id': self.message_id,
                        'block_id': self.block_counter,
                        'language': language,
                        'code': code
                    })
                    new_lines.append(rendered_block)
                    in_code_block = False
                    self.block_counter += 1
                else:
                    # Start of code block
                    in_code_block = True
                    language = line.strip()[3:] or 'plaintext'
                    code_block_lines = []
            elif in_code_block:
                code_block_lines.append(line)
            else:
                new_lines.append(line)

        return new_lines

class CodeBlockExtension(markdown.Extension):
    def __init__(self, message_id, **kwargs):
        self.config = {'message_id': message_id}
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.preprocessors.register(CodeBlockPreprocessor(self.config['message_id']), 'code_block', 25)