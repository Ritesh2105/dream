from datetime import datetime
import random
from pprint import pformat

from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin

class CapacityProjectGantt(plugin.OutputPreparationPlugin, TimeSupportMixin):

  def _generateRandomTaskList(self):
    """Generate some random tasks for the example.

    Take care of not using reserved id '0'
    """
    for order_id in range(3):
      for order_line_id in range(random.randint(1, 6)):
        start_time = random.random() * 10
        duration = random.random() * 10
        yield dict(id='%s_%s' % (order_id, order_line_id),
                   order_id="O%s" % order_id,
                   start_time=start_time,
                   duration=duration)

  def postprocess(self, data):
    """Post process the data for Gantt gadget
    """
    print 1
    data['general']['dateFormat']='%Y/%m/%d'
    self.initializeTimeSupport(data)
    date_format = '%d-%m-%Y %H:%M'
    resultElements=data['result']['result_list'][-1]['elementList']
    task_dict = {}
    for element in resultElements:
      if element['_class']=="Dream.CapacityProject":
        # add the project in the gantt
        task_dict[element['id']] = dict(
        id=element['id'],
        text='Project %s' % element['id'],
        type='project',
        open=False)
            
        projectSchedule=element['results'].get('schedule',{})
        for record in projectSchedule:
            task_dict[element['id']+record['stationId']] = dict(
                id=record['stationId'],
                parent=element['id'],
                text=record['stationId'],
                start_date=self.convertToRealWorldTime(
                      record['entranceTime']).strftime(date_format),
                stop_date=self.convertToRealWorldTime(
                      record['exitTime']).strftime(date_format),
                open=False,
                duration=int(record['exitTime'])-int(record['entranceTime'])
            )
        
    # return the result to the gadget
    result = data['result']['result_list'][-1]
    result[self.configuration_dict['output_id']] = dict(
      time_unit=self.getTimeUnitText(),
      task_list=sorted(task_dict.values(),
        key=lambda task: (task.get('id'),
                          task.get('type') == 'project',
                          task.get('start_date'))))
    import json
    outputJSONString=json.dumps(task_dict, indent=5)
    outputJSONFile=open('task_dict.json', mode='w')
    outputJSONFile.write(outputJSONString)
    return data
    
# 
#     date_format = '%d-%m-%Y %H:%M'
# 
#     task_dict = {}
#     for task in self._generateRandomTaskList():
# 
#       # Add the order if not already present
#       if task['order_id'] not in task_dict:
#         task_dict[task['order_id']] = dict(
#           id=task['order_id'],
#           text='Order %s' % task['order_id'],
#           type='project',
#           open=True)
# 
#       task_dict[task['id']] = dict(
#           id=task['id'],
#           parent=task['order_id'],
#           text='Task %s' % task['id'],
#           start_date=self.convertToRealWorldTime(
#             task['start_time']).strftime(date_format),
#           stop_date=self.convertToRealWorldTime(
#             task['start_time'] + task['duration']).strftime(date_format),
#           open=True,
#           duration=task['duration'])
# 
#     result = data['result']['result_list'][-1]
#     result[self.configuration_dict['output_id']] = dict(
#       time_unit=self.getTimeUnitText(),
#       task_list=sorted(task_dict.values(),
#         key=lambda task: (task.get('order_id'),
#                           task.get('type') == 'project',
#                           task.get('start_date'))))
# 
#     return data
