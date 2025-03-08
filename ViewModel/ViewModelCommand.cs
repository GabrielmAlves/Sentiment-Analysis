using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;

namespace PlayerClassifier.WPF.ViewModel
{
    public class ViewModelCommand : ICommand
    {
        private readonly Action<object> _executeAction; //encapsula um método, ou seja, pode passar ele por parâmetro
        private readonly Predicate<object> _canExecuteAction; //determina se a ação pode ser feita ou não

        //construtores

        public ViewModelCommand(Action<object> executeAction) //para executar a ação, já que nem todos comandos precisam ser validados
        {
            _executeAction = executeAction;
            _canExecuteAction = null;
        }
        public ViewModelCommand(Action<object> executeAction, Predicate<object> canExecuteAction)
        {
            _executeAction = executeAction;
            _canExecuteAction = canExecuteAction;
        }
        //eventos
        public event EventHandler? CanExecuteChanged
        {
            add { CommandManager.RequerySuggested += value; }
            remove { CommandManager.RequerySuggested -= value; }                                         //esse evento (RequerySuggested) acontece quando o CommandManager detecta que a condição CommandExecution 
        }                                                                                                  //mudou

        //métodos
        public bool CanExecute(object? parameter) //se o _canExecute for (null), retorna true pq a validação do predicate não foi estabelecida. se não, retorna o valor 
        {                                         //do delegate, ou seja, o método que vai ser definido e delegado na ViewModel  
            return _canExecuteAction == null ? true : _canExecuteAction(parameter);
        }

        public void Execute(object? parameter)
        {
            _executeAction(parameter); //executa a ação, vai executar o método que vai ser delegado a ViewModel
        }
    }
}