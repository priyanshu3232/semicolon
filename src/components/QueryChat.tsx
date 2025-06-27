import React, { useState, useRef } from 'react';
import { Send, Mic, MicOff, Bot, User, Loader, Clock, FileText } from 'lucide-react';
import { useQueryDocuments, useSpeechToText } from '../hooks';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Array<{
    document_id: string;
    filename: string;
    similarity_score: number;
    excerpt: string;
  }>;
  processingTime?: number;
}

const QueryChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: 'Hello! I can help you find information from your uploaded documents. What would you like to know?',
      timestamp: new Date(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const queryDocuments = useQueryDocuments();
  const speechToText = useSpeechToText();

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');

    // Query documents
    queryDocuments.mutate(
      { question: inputMessage },
      {
        onSuccess: (response) => {
          const assistantMessage: Message = {
            id: (Date.now() + 1).toString(),
            type: 'assistant',
            content: response.answer,
            timestamp: new Date(),
            sources: response.sources,
            processingTime: response.processing_time,
          };
          setMessages(prev => [...prev, assistantMessage]);
        },
        onError: (error) => {
          const errorMessage: Message = {
            id: (Date.now() + 1).toString(),
            type: 'assistant',
            content: `Sorry, I encountered an error: ${error.message}`,
            timestamp: new Date(),
          };
          setMessages(prev => [...prev, errorMessage]);
        },
      }
    );
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const audioFile = new File([audioBlob], 'recording.wav', { type: 'audio/wav' });
        
        speechToText.mutate(
          { audioFile },
          {
            onSuccess: (response) => {
              setInputMessage(response.transcript);
            },
            onError: (error) => {
              console.error('Speech-to-text error:', error);
            },
          }
        );
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg flex flex-col h-[600px]">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-2xl font-bold text-gray-900">Document Chat</h2>
        <p className="text-gray-600 mt-1">Ask questions about your uploaded documents</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-4 ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <div className="flex items-start space-x-3">
                <div className={`p-1 rounded-full ${
                  message.type === 'user' ? 'bg-blue-700' : 'bg-gray-200'
                }`}>
                  {message.type === 'user' ? (
                    <User className="w-4 h-4" />
                  ) : (
                    <Bot className="w-4 h-4" />
                  )}
                </div>
                
                <div className="flex-1">
                  <p className="text-sm leading-relaxed">{message.content}</p>
                  
                  {/* Processing time */}
                  {message.processingTime && (
                    <div className="flex items-center space-x-1 mt-2 text-xs opacity-75">
                      <Clock className="w-3 h-3" />
                      <span>{message.processingTime.toFixed(2)}s</span>
                    </div>
                  )}
                  
                  {/* Sources */}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <p className="text-xs font-medium opacity-75">Sources:</p>
                      {message.sources.map((source, index) => (
                        <div
                          key={index}
                          className="bg-black bg-opacity-10 rounded p-2 text-xs"
                        >
                          <div className="flex items-center space-x-1">
                            <FileText className="w-3 h-3" />
                            <span className="font-medium">{source.filename}</span>
                            <span className="opacity-75">
                              (Score: {source.similarity_score.toFixed(2)})
                            </span>
                          </div>
                          <p className="mt-1 opacity-75">{source.excerpt}</p>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  <p className="text-xs opacity-50 mt-2">
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {queryDocuments.isPending && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <Loader className="w-4 h-4 animate-spin" />
                <span className="text-sm text-gray-600">Searching documents...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-6 border-t border-gray-200">
        <div className="flex items-end space-x-3">
          <div className="flex-1">
            <div className="flex items-center space-x-2 bg-gray-50 rounded-lg p-3">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask a question about your documents..."
                rows={1}
                className="flex-1 bg-transparent border-none resize-none focus:outline-none"
              />
              
              <button
                onClick={isRecording ? stopRecording : startRecording}
                disabled={speechToText.isPending}
                className={`p-2 rounded-full transition-colors ${
                  isRecording
                    ? 'bg-red-100 text-red-600 hover:bg-red-200'
                    : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                }`}
              >
                {speechToText.isPending ? (
                  <Loader className="w-5 h-5 animate-spin" />
                ) : isRecording ? (
                  <MicOff className="w-5 h-5" />
                ) : (
                  <Mic className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>
          
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || queryDocuments.isPending}
            className="bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default QueryChat;
